from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View, ListView, DetailView
from django.core.mail import send_mail

from .models import Installation, Contact, Product
from .forms import ContractorForm
from .kashflow import KashFlow
from .zoho import Zoho
from emails.views import send_provisional_date, \
send_installation_and_delivery_form, send_confirmation_email, \
send_retailer_pickup_date, send_installation_exists_notifier

from datetime import date, timedelta

class InstallationList(ListView):
    model = Installation

class InstallationDetail(DetailView):
    model = Installation

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
        send_provisional_date(date=installation.provisional_date, yes=yes_link, no=no_link)
        return HttpResponse("Installation successfully added")


    def add_installation(self, pot_data):
        installation = Installation(
                id=pot_data.get('potential_id', ''),
                name=pot_data.get('potential_name', ''),
                address_one=pot_data.get('site_address', ''),
                address_two=pot_data.get('site_address_two', ''),
                postcode=pot_data.get('site_postcode', ''))
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
            product = Product(
                name=item[0],
                quantity=item[1],
                installation=Installation.objects.get(id=inst_pk))
            product.save()
            print "Added product : ", product

class ContractorConfirmation(View):
    def get(self, request, *args, **kwargs):
        installation_id = self.kwargs.get('installation_id')
        installation = Installation.objects.get(id=installation_id)
        answer = request.GET.get('confirm')
        base_url = 'http://localhost:8080/installations/'
        department = "/contractor/"
        dates_form_link = base_url + installation_id + department + 'form/'

        if answer == 'yes':
            installation.contractor_confirmed = True
            send_installation_and_delivery_form(
                    answer=answer,
                    date=installation.provisional_date,
                    site_name=installation.name,
                    name=installation.contact_set.first().name,
                    number=installation.contact_set.first().phone,
                    email=installation.contact_set.first().email,
                    form=dates_form_link)
            return HttpResponse("Thank you for confirming the provisional week, you will be \
                    sent an email with the customers details so that you can get in touch \
                    with them to arrange suitable installation and delivery dates. \
                    Please fill in the form linked in the email.")

        else:
            #redirect contractor to form to pick date that suits them
            print "contractor not confirmed"
            installation.contractor_confirmed = False
            send_installation_and_delivery_form(
                    answer=answer,
                    date=installation.provisional_date,
                    site_name=installation.name,
                    name=installation.contact_set.first().name,
                    number=installation.contact_set.first().phone,
                    email=installation.contact_set.first().email,
                    form=dates_form_link)
            return HttpResponse("Thank you for your honesty, you have been sent another email \
                    with the customers details so that you can get in touch with them to \
                    arrange suitable installation and delivery dates. Please fill in the form \
                    linked in the email.")

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
            installation.save()
            installation.set_pickup()
            send_confirmation_email(
                site_name=installation.name,
                delivery_date=delivery_date,
                installation_date=installation_date)
            #send purchase order
            kf = KashFlow()
            purchase_order = kf.create_purchase_order(installation.name)
            for product in installation.product_set.all():
                kf.add_item(purchase_order, product.quantity,settings.SALES_CODE, product.name, product.rate)
            kf.add_delivery_address(purchase_order,
                    '\n%s, \n%s, \n%s, \n%s' % (installation.name,
                                                installation.address_one,
                                                installation.address_two,
                                                installation.postcode))
            po_confirmation = kf.send_purchase_order(purchase_order)
            base_url = 'http://localhost:8080/installations/'
            department = "/retailer/"
            pk = installation.id
            yes_link = base_url + pk + department + "?confirm=yes"
            no_link = base_url + pk + department + "?confirm=no"
            send_retailer_pickup_date(
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
            {'form': form,
            'installation_id': installation_id,
            'site_name': installation.name})

class RetailerConfirmation(View):
    def get(self, request, *args, **kwargs):
        installation_id = self.kwargs.get('installation_id')
        installation = Installation.objects.get(id=installation_id)
        answer = request.GET.get('confirm')
        if answer == 'yes':
            installation.retailer_confirmed = True
            kf = KashFlow(supplier='Kuehne + Nagel', supplier_id=2876893)
            purchase_order = kf.create_purchase_order('some ref')
            kf.add_item(purchase_order, 1.00, settings.CARRRIAGE, 'KL1 + STK', 2700.00)
            kf.add_delivery_address(purchase_order,'\nFlat 1, \n25 Crescent Way, \nBrockey, \nSE4 1QL')
            po_confirmation = kf.send_purchase_order(purchase_order)
        else:
            #redirect contractor to form to pick date that suits them
            print "contractor not confirmed"
            installation.retailer_confirmed = False

        return HttpResponse(installation.retailer_confirmed)
