from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View, ListView, DetailView
from django.core.mail import send_mail

from datetime import date, timedelta

from .models import Installation, Contact

import urllib
import urllib2
import json
import pprint

class InstallationList(ListView):
    model = Installation

class InstallationDetail(DetailView):
    model = Installation

class CreateInstallation(View):
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
        if not Installation.objects.get(pk=potential_data['potential_id']):
            self.add_contact(contact_data)
            self.add_installation(potential_data, contact_data)
        """
        send email to contractor
        """
        def next_weekday(day, weekday):
            days_ahead = weekday - day.weekday()
            if days_ahead <= 0: # Target day already happened this week
                days_ahead += 7
            return day + timedelta(days_ahead)
        installation = Installation.objects.get(pk=potential_data['potential_id'])
        provisional_date = installation.created_date
        print "date created: ", provisional_date
        prov_date_buffer = timedelta(days=42)
        provisional_date += prov_date_buffer
        print "6 weeks ahead : ", provisional_date
        provisional_date = next_weekday(provisional_date, 0)
        print "next monday from date: ", provisional_date

        body="""
Hi Jake,

An order has come through for a toilet installation, could you please confirm that the week beginning %s is ok for you for an installation?
Please confirm by clicking the below link.

<a href="%s">YES</a>

Otherwise to choose another week click the following link.

<a hfre="%s">NO</a>

Thanks,

Woo Woo Web App
""" % (provisional_date, provisional_date, provisional_date)

        send_mail('Please confirm this provisional date',
                body,
                'auto@waterlesstoilet.co.uk',
                ['contractor@waterlesstoilets.co.uk'],
                fail_silently=False)

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
            return data['response']['result'][module_name]['row']['FL']
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

            if value == 'POTENTIALID':
                p_data['potential_id'] = content
            elif value == 'Potential Name':
                p_data['potential_name'] = content
            elif value == 'Site Street':
                p_data['site_address'] = content
            elif value == 'Site Street 2':
                p_data['site_address_two'] = content
            elif value == 'Site Post Code':
                p_data['site_postcode'] = content
            elif value == 'CONTACTID':
                p_data['contact_id'] = content

        return p_data

    def extract_contact_data(self, contact_json):
        """
        extract the potential data we need for our models
        """
        c_data = {}
        for set in contact_json:
            value = set['val']
            content = set['content']

            if value == 'CONTACTID':
                c_data['contact_id'] = content
            elif value == 'First Name':
                c_data['first_name'] = content
            elif value == 'Last Name':
                c_data['last_name'] = content
            elif value == 'Phone':
                c_data['phone'] = content
            elif value == 'Email':
                c_data['email'] = content

        return c_data

    def add_contact(self, data):
        contact = Contact(
                id = data['contact_id'],
                name = data['first_name']+" "+data['last_name'],
                phone = data['phone'],
                email = data['email'])
        contact.save()
        print "Added contact : ", contact

    def add_installation(self, pot_data, con_data):
        contact = Contact.objects.get(pk=con_data['contact_id'])
        installation = Installation(
                id = pot_data['potential_id'],
                name = pot_data['potential_name'],
                address_one = pot_data['site_address'],
                address_two = pot_data['site_address_two'],
                postcode = pot_data['site_postcode'],
                contacts = contact)
        installation.save()
        print "Added installation at site : ", installation

class ContractorConfirmation(View):
    def get(self, request):
        answer = request.GET.get('confirm')
        return HttpResponse(answer)
