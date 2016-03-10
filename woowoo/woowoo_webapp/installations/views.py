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
from emails.views import send_provisional_date, \
send_installation_and_delivery_form, send_confirmation_email, \
send_supplier_pickup_date, send_installation_exists_notifier, \
send_all_dates_confirmation, send_manager_notification_email, \
send_confirmation_to_contact

from datetime import date, timedelta

class InstallationList(LoginRequiredMixin, ListView):
    model = Installation

class InstallationDetail(LoginRequiredMixin, DetailView):
    model = Installation

    def get_context_data(self, **kwargs):
        context = super(InstallationDetail, self).get_context_data(**kwargs)
        context['status'] = context['installation'].get_status()
        context['contact'] = context['installation'].contact_set.first()
        context['gmap_url'] = context['installation'].get_gmaps_url()
        return context

class CreateInstallation(View):
    def get(self, request):
        zoho = Zoho()
        """retrieve and extract potential data"""
        potential_id = request.GET.get('pid')
        potential = zoho.get_record_data("Potentials", potential_id)
        potential_data = zoho.extract_potential_data(potential)

        """retrieve and extract contact data"""
        contact = zoho.get_record_data("Contacts", potential_data.get('contact_id'))
        contact_data = zoho.extract_contact_data(contact)

        """extract product data"""
        products = zoho.extract_product_data(potential)

        """create instances with data"""
        matches = Installation.objects.filter(pk=potential_data['potential_id'])
        if matches.count() < 1:
            installation_pk = self.add_installation(potential_data)
            self.add_contact(contact_data, installation_pk)
            self.add_product(products, installation_pk)
        else:
            print "Installation with that potential ID has already been added"
            match = matches.first()
            send_installation_exists_notifier(recipient=settings.MANAGER, installation=match, pid=potential_id)
            return HttpResponse('Installation already exisits with that ID', status=202)

        pk = potential_data['potential_id']
        installation = Installation.objects.get(pk=pk)

        """email links for contractor"""
        base_url = settings.SITE_URL + 'installations/'
        department = "/contractor/"
        yes_link = base_url + pk + department + "?confirm=yes"
        no_link = base_url + pk + department + "?confirm=no"

        if "GG" in installation.installation_method:
            send_provisional_date(date=installation.provisional_date,
                    yes=yes_link,
                    no=no_link,
                    recipient=settings.CONTRACTOR,
                    email_to=settings.CONTRACTOR_EMAIL)
        else:
            send_provisional_date(date=installation.provisional_date,
                    yes=yes_link,
                    no=no_link,
                    recipient=settings.MANAGER,
                    email_to=settings.MANAGER_EMAIL)
        return HttpResponse("Installation successfully added")


    def add_installation(self, pot_data):
        forklift = pot_data.get('forklift', '')
        if forklift == 'true':
            forklift = True
        else:
            forklift = False

        installation = Installation(
                id=pot_data.get('potential_id', ''),
                name=pot_data.get('potential_name', ''),
                address_one=pot_data.get('site_address', ''),
                address_two=pot_data.get('site_address_two', ''),
                city=pot_data.get('site_city', ''),
                county=pot_data.get('site_county', ''),
                postcode=pot_data.get('site_postcode', ''),
                forklift_available=forklift,
                installation_method=pot_data.get('install_method', ''),
                gmaps_link=pot_data.get('gmap_link', ''),
                long_and_lat=pot_data.get('long_lat', ''))
        installation.save()
        print "Added installation at site : ", installation
        return installation.id

    def add_contact(self, data, inst_pk):
        contact = Contact(
                id=data.get('contact_id',''),
                name=data.get('first_name', '')+" "+data.get('last_name', ''),
                phone=data.get('phone',''),
                email=data.get('email',''),
                installation=Installation.objects.get(id=inst_pk))
        contact.save()
        print "Added contact : ", contact

    def add_product(self, data, inst_pk):
        for item in data.items():
            if int(item[1]) > 0:
                product = Product(
                    name=item[0],
                    quantity=item[1],
                    installation=Installation.objects.get(id=inst_pk))
                product.save()
                print "Added product : ", product

class ContractorConfirmation(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        installation_id = self.kwargs.get('installation_id')
        installation = Installation.objects.get(id=installation_id)
        answer = request.GET.get('confirm')
        base_url = settings.SITE_URL + 'installations/'
        department = "/contractor/"
        dates_form_link = base_url + installation_id + department + 'form/'

        if answer == 'yes':
            installation.contractor_confirmed = True
        else:
            installation.contractor_confirmed = False
        send_installation_and_delivery_form(
                answer=answer,
                date=installation.provisional_date,
                site_name=installation.name,
                name=installation.contact_set.first().name,
                number=installation.contact_set.first().phone,
                email=installation.contact_set.first().email,
                form=dates_form_link)

        return render(request, 'installations/contractor_confirmation.html',
                    context={"name": settings.MANAGER,
                             "form" : dates_form_link,
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
            send_confirmation_email(
                site_name=installation.name,
                delivery_date=delivery_date,
                installation_date=installation_date)

            kf = KashFlow(
                    recipient=settings.KF_SUPPLIER_NAME,
                    recipient_id=settings.KF_SUPPLIER_ID)
            purchase_order = kf.create_purchase_order(installation.name)
            for product in installation.product_set.all():
                if product.quantity > 0:
                    kf.add_item(purchase_order, product.quantity, settings.SALES_CODE, product.name, product.rate)
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
            base_url = settings.SITE_URL + 'installations/'
            department = "/supplier/"
            pk = installation.id
            yes_link = base_url + pk + department + "?confirm=yes"
            no_link = base_url + pk + department + "?confirm=no"
            send_supplier_pickup_date(
                    site_name=installation.name,
                    pickup_date=installation.pickup_date.strftime('%d/%m/%Y'),
                    yes_link=yes_link,
                    no_link=no_link)
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
            send_all_dates_confirmation(installation)
        else:
            installation.supplier_confirmed = False
            installation.save()
            send_manager_notification_email(installation.name, installation.pickup_date)

        return render(request, 'installations/supplier_form_redirect.html',
                context={"confirmation": installation.supplier_confirmed,
                         "name" : settings.MANAGER })
@login_required
def notify_contact(request, *args, **kwargs):
    installation_id = kwargs.get('installation_id')
    installation=Installation.objects.get(id=installation_id)
    send_confirmation_to_contact(installation)
    return HttpResponse('Email has been sent to customer ;-) Now you can relax', status=202)
