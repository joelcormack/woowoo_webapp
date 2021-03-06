from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View, ListView, DetailView
from django.core.mail import send_mail
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .models import Installation, Contact, Product
from .forms import ContractorForm
from .kashflow import KashFlow
from .zoho import Zoho
from emails.views import send_confirmation_to_contact
import datetime
from datetime import date, timedelta

class InstallationList(LoginRequiredMixin, ListView):
	"""list all installations that have not yet happened"""
	context_object_name = 'installation'
        week = timedelta(days=7)
	queryset = Installation.objects.filter(
                installation_date__gte=datetime.date.today() - week,
                installation_method='GG'
                )

class InstallationDetail(LoginRequiredMixin, DetailView):
    model = Installation

    def get_context_data(self, **kwargs):
        context = super(InstallationDetail, self).get_context_data(**kwargs)
        context['status'] = context['installation'].get_status()
        context['contact'] = context['installation'].contact_set.first()
        context['products'] = context['installation'].product_set.all()
        context['gmap_url'] = context['installation'].get_gmaps_url()
        return context

class CreateInstallation(View):
    def get(self, request):
        zoho = Zoho()
        """retrieve and extract potential data"""
        potential_id = request.GET.get('pid')
        potential = zoho.get_record("Potentials", potential_id)
        potential_data = zoho.extract(potential, settings.POTENTIAL_TO_INSTALLATION)

        """retrieve and extract contact data"""
        contact = zoho.get_record("Contacts", potential_data.get('contact_id'))
        contact_data = zoho.extract(contact, settings.ZOHO_CONTACT_TO_CONTACT)
        """extract product data"""
        products = zoho.extract(potential, settings.PRODUCTS)

        """create instances with data"""
        pk = potential_data['potential_id']
        matches = Installation.objects.filter(pk=pk)
        if matches:
            print "Installation with that potential ID has already been added"
            match = matches.first()
            match.send_installation_exists_notifier()
            return HttpResponse('Installation already exisits with that ID', status=202)
        else:
            installation = Installation.objects.create_installation(potential_data)
            contact = Contact.objects.create_contact(contact_data, installation)
            product = Product.objects.create_product(products, installation)
            #save em
            installation.save()
            contact.save()
            product.save()
            installation = Installation.objects.get(pk=pk)
            installation.send_provisional_date_notification()
            return HttpResponse("Installation successfully added")

class ContractorConfirmation(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        installation_id = self.kwargs.get('installation_id')
        installation = Installation.objects.get(id=installation_id)
        answer = request.GET.get('confirm')

        if answer == 'yes':
            installation.contractor_confirmed = True
        else:
            installation.contractor_confirmed = False

        installation.send_date_form_notification(answer=answer)

        return render(request, 'installations/contractor_confirmation.html',
                    context={"name": settings.MANAGER,
                             "form" : installation.link('/contractor/', 'form/'),
                             "confirmation" : installation.contractor_confirmed})


@login_required
def set_dates(request, *args, **kwargs):

    installation_id = kwargs.get('installation_id')
    installation=Installation.objects.get(id=installation_id)

    if request.method == 'POST':
        form = ContractorForm(request.POST)
        if form.is_valid():
            installation_date = form.cleaned_data.get('installation_date')
            delivery_date = form.cleaned_data.get('delivery_date')
            installation = Installation.objects.get(id=installation_id)
            installation.delivery_date = delivery_date
            installation.installation_date = installation_date
            installation.contractor_confirmed = True
            installation.customer_confirmed = True
            installation.save()
            installation.set_pickup()
            installation.send_confirmation_notification()

            kf = KashFlow(
                    recipient=settings.KF_SUPPLIER_NAME,
                    recipient_id=settings.KF_SUPPLIER_ID)
            purchase_order = kf.create_purchase_order(installation.name)
            for product in installation.product_set.all():
                if product.quantity > 0:
                    kf.add_item(purchase_order, product.quantity, settings.SALES_CODE, product.name, product.get_rate())
            kf.add_note(purchase_order,
                    'Delivery Address:\n%s, \n%s, \n%s, \n%s, \n%s, \n%s' % (installation.name,
                                                                 installation.address_one,
                                                                 installation.address_two,
                                                                 installation.city,
                                                                 installation.county,
                                                                 installation.postcode))
            kf.add_note(purchase_order,
                    'Contact: %s %s' % (installation.contact_set.first().name, installation.contact_set.first().phone))
            content = """
Dear Kazuba SARL,

Please find attached the Purchase Order %s

We would like to arrange collection for %s

Please confirm that we are able to collect it on this date by replying to the other email we have sent you.

Kind regards,

Accounts

WooWoo
""" % (purchase_order, installation.pickup_date)

            po_confirmation = kf.send_purchase_order(
                    purchase_order,
                    settings.APPLICATION_ACCOUNTS_EMAIL,
                    settings.APPLICATION_ACCOUNTS_NAME,
                    'Email Purchases %s' % purchase_order,
                    content,
                    settings.KF_SUPPLIER_EMAIL)
            installation.send_supplier_pickup_date_notification()
            return HttpResponseRedirect(reverse('installation-detail', kwargs={'pk': installation_id}))
    else:
        form = ContractorForm()
    return render(
            request,
            'installations/installation_dates.html',
            context={'form': form,
            'installation_id': installation_id,
            'site_name': installation.name})

class SupplierConfirmation(View):


    def get(self, request, *args, **kwargs):
        DESCRIPTION ="""Pallet Shipment
Dimensions: 235 cm long x 105cm wide
Weight: 350kg
        """
        installation_id = self.kwargs.get('installation_id')
        installation = Installation.objects.get(id=installation_id)
        answer = request.GET.get('confirm')
        loading_date = installation.pickup_date
        unloading_date = installation.delivery_date
        if answer == 'yes':
            installation.supplier_confirmed = True
            installation.save()
            kf = KashFlow(recipient=settings.KF_SHIPPING_COMPANY,
                    recipient_id=settings.KF_SHIPPING_COMPANY_ID)
            purchase_order = kf.create_purchase_order()
            kf.add_item(purchase_order, installation.product_set.count(), settings.CARRIAGE, DESCRIPTION, 0)
            kf.add_note(purchase_order, 'Loading Date: %s \nUnloading Date: %s' %(loading_date, unloading_date))
            kf.add_note(purchase_order, 'Loading: \n\
SARL Kazuba \n\
18, Chemin du trou de Fourque \n\
13200 Arles \n\
Contact: Nicolas Flamen +33(0)6 28 33 10 89')
            kf.add_note(purchase_order, 'Unloading: \n%s, \n%s, \n%s, \n%s, \n%s, \n%s' % (installation.name,
                installation.address_one,
                installation.address_two,
                installation.city,
                installation.county,
                installation.postcode))
            kf.add_note(purchase_order, 'Contact: %s - %s' % (installation.contact_set.first(), installation.contact_set.first().phone))
            if installation.forklift_available:
                kf.add_note(purchase_order, 'Delivery Instructions: Customer has forklift.')
            else:
                kf.add_note(purchase_order, "Delivery Instructions: Customer doesn't have a forklift.")

            content = """
Dear Kuehne + Nagel,

Please find attached the Purchase Order %s.

We would like to arrange collection.

Please confirm the price and dates for loading/unloading.
""" % purchase_order


            po_confirmation = kf.send_purchase_order(
                    purchase_order,
                    settings.APPLICATION_SHIPPING_EMAIL,
                    settings.APPLICATION_SHIPPING_NAME,
                    'Transportation Order - %s' % purchase_order,
                    content,
                    settings.KF_SHIPPING_EMAIL_TO)
            installation.send_all_dates_notification()
        else:
            installation.supplier_confirmed = False
            installation.save()
            installaion.send_manager_notification()

        return render(request, 'installations/supplier_form_redirect.html',
                context={"confirmation": installation.supplier_confirmed,
                         "name" : settings.MANAGER })
@login_required
def notify_contact(request, *args, **kwargs):
    installation_id = kwargs.get('installation_id')
    installation=Installation.objects.get(id=installation_id)
    installation.send_confirmation_to_contact()
    return HttpResponse('Email has been sent to customer ;-) Now you can relax', status=202)
