from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View, ListView, DetailView
from django.core.mail import send_mail

from datetime import date, timedelta

from .models import Installation, Contact
from .forms import ContractorForm
from .mailing import send_provisional_date, \
send_installation_and_delivery_form, send_confirmation_email

import urllib
import urllib2
import json
import pprint

class InstallationList(ListView):
    model = Installation

class InstallationDetail(DetailView):
    model = Installation

class CreateInstallation(View):
    potential_to_installation = {
                'POTENTIALID':'potential_id',
                'Potential Name':'potential_name',
                'Site Street':'site_address',
                'Site Street 2':'site_address_two',
                'Site Post Code':'site_postcode',
                'CONTACTID':'contact_id'}
    contact_zoho_to_contact = {
                'CONTACTID' : 'contact_id',
                'First Name': 'first_name',
                'Last Name': 'last_name',
                'Phone' : 'phone',
                'Email': 'email'}

    def get(self, request):
        """
        retrieve and extract data
        """
        potential_id = request.GET.get('pid')
        potential = self.get_record_data("Potentials", potential_id)
        potential_data = self.extract_potential_data(potential)
        contact = self.get_record_data("Contacts", potential_data.get('contact_id'))
        contact_data = self.extract_contact_data(contact)
        pretty_data = pprint.pformat(potential_data) + pprint.pformat(contact_data)
        """
        create instances with data
        """
        matches = Installation.objects.filter(pk=potential_data['potential_id'])
        if matches.count() < 1:
            self.add_contact(contact_data)
            self.add_installation(potential_data, contact_data)
        """
        create provisional date
        """
        def next_weekday(day, weekday):
            days_ahead = weekday - day.weekday()
            if days_ahead <= 0: # Target day already happened this week
                days_ahead += 7
            return day + timedelta(days_ahead)
        pk = potential_data['potential_id']
        installation = Installation.objects.get(pk=pk)
        provisional_date = installation.created_date
        print "date created: ", provisional_date
        prov_date_buffer = timedelta(days=42)
        provisional_date += prov_date_buffer
        print "6 weeks ahead : ", provisional_date
        provisional_date = next_weekday(provisional_date, 0)
        installation.provisional_date = provisional_date
        installation.save()
        print "next monday from date: ", provisional_date
        """
        email links for contractor
        """
        base_url = 'http://localhost:8080/installations/'
        department = "/contractor/"
        yes_link = base_url + pk + department + "?confirm=yes"
        no_link = base_url + pk + department + "?confirm=no"
        links = (provisional_date,yes_link, no_link)
        send_provisional_date(links)
        return HttpResponse("ok")

    def get_record_data(self, module_name, record_id):
        """
        retieves potential data in json format
        from zoho api and returns a python dictionary
        """
        authtoken = settings.ZOHO_AUTHTOKEN
        params = {'authtoken':authtoken,'scope':'crmapi','id':record_id}
        final_URL = "https://crm.zoho.com/crm/private/json/"+module_name+"/getRecordById"
        data = urllib.urlencode(params)
        request = urllib2.Request(final_URL,data)
        response = urllib2.urlopen(request)
        json_response = response.read()
        data = json.loads(json_response)
        try:
            data = data['response']['result'][module_name]['row']['FL']
            return data
        except ValueError, Argument:
            print "Incorrect json response structure from zoho API", Argument

    def extract_potential_data(self, potential_json):
        """
        extract the potential data we need for our models
        """
        p_data = {}
        for set in potential_json:
            value = set['val']
            content = set['content']
            for pot, ins in CreateInstallation.potential_to_installation.iteritems():
                if value == pot:
                    p_data[ins] = content

        return p_data

    def extract_contact_data(self, contact_json):
        """
        extract the potential data we need for our models
        """
        c_data = {}
        for set in contact_json:
            value = set['val']
            content = set['content']
            for contact_zoho, contact in CreateInstallation.contact_zoho_to_contact.iteritems():
                if value == contact_zoho:
                    c_data[contact] = content

        return c_data

    def add_contact(self, data):
        contact = Contact(
                id = data.get('contact_id',''),
                name = data.get('first_name', '')+" "+data.get('last_name', ''),
                phone = data.get('phone',''),
                email = data.get('email',''))
        contact.save()
        print "Added contact : ", contact

    def add_installation(self, pot_data, con_data):
        contact = Contact.objects.get(pk=con_data['contact_id'])
        installation = Installation(
                id = pot_data.get('potential_id', ''),
                name = pot_data.get('potential_name', ''),
                address_one = pot_data.get('site_address', ''),
                address_two = pot_data.get('site_address_two', ''),
                postcode = pot_data.get('site_postcode', ''),
                contacts = contact)
        installation.save()
        print "Added installation at site : ", installation

class ContractorConfirmation(View):
    def get(self, request, *args, **kwargs):
        installation_id = self.kwargs.get('installation_id')
        installation = Installation.objects.get(id=installation_id)
        answer = request.GET.get('confirm')
        if answer == 'yes':
            installation.contractor_confirmed = True
            base_url = 'http://localhost:8080/installations/'
            department = "/contractor/"
            dates_form_link = base_url + installation_id + department + 'form/'
            links = (installation.provisional_date, dates_form_link)
            send_installation_and_delivery_form(links)
        else:
            #redirect contractor to form to pick date that suits them
            print "contractor not confirmed"

        return HttpResponse(installation.contractor_confirmed)

def get_dates(request, *args, **kwargs):
    installation_id = kwargs.get('installation_id')
    if request.method == 'POST':
        form = ContractorForm(request.POST)
        if form.is_valid():
            installation_date = form.cleaned_data.get('installation_date')
            delivery_date = form.cleaned_data.get('delivery_date')
            installation = Installation.objects.get(id=installation_id)
            installation.delivery_date = delivery_date
            installation.installation_date = installation_date
            installation.save()
            send_confirmation_email((installation.name, installation.name, delivery_date, installation_date))
            return HttpResponseRedirect(reverse('installation-detail', kwargs={'pk': installation_id}))
    else:
        form = ContractorForm()
    return render(
            request,
            'installations/installation_dates.html',
            {'form': form,
            'installation_id': installation_id})
