from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View, ListView, DetailView
from .models import Installation, Site, Contact

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
        retireve and extract data
        """
        potential_id = request.GET.get('pid')
        potential = self.get_record_data("Potentials", potential_id)
        potential_data = self.extract_potential_data(potential)
        contact = self.get_record_data("Contacts", potential_data.get('contact_id'))
        contact_data = self.extract_contact_data(contact)
        pretty_data = pprint.pformat(potential_data) + pprint.pformat(contact_data)
        """
        create instaces with data
        """
        self.add_site(potential_data)
        return HttpResponse(pretty_data)

    def get_record_data(self, module_name, record_id):
        """
        retieves potential data in json format
        using zoho api and returns python dictionary
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
        p_data = {}
        for set in potential_json:
            value = set['val']
            content = set['content']

            if value == 'Potential Name':
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
        c_data = {}
        for set in contact_json:
            value = set['val']
            content = set['content']

            if value == 'First Name':
                c_data['first_name'] = content
            elif value == 'Last Name':
                c_data['last_name'] = content
            elif value == 'Phone':
                c_data['phone'] = content
            elif value == 'Email':
                c_data['email'] = content

        return c_data
    def add_site(self, data):
        site = Site(
                name = data['potential_name'],
                address_one = data['site_address'],
                address_two = data['site_address_two'],
                postcode = data['site_postcode'])
        site.save()
        print site
