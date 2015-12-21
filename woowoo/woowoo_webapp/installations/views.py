from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View, ListView, DetailView
from django.core.mail import send_mail

from datetime import date, timedelta

from .models import Installation, Contact
from .forms import ContractorForm
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
        print "next monday from date: ", provisional_date
        """
        email links for contractor
        """
        base_url = 'http://localhost:8080/installations/'
        contractor = "/contractor/"
        yes_link = base_url + pk + contractor + "?confirm=yes"
        no_link = base_url + pk + contractor + "?confirm=no"
        """
        send email to contractor
        """
        body="""
Hi Jake,

We've received an order. The provisional week for delivery is %s (6 weeks from now).

Please confirm this is a good week for you to install.

<a href="%s">YES</a>

<a hfre="%s">NO</a>

Thanks,

Woo Woo Web App
""" % (provisional_date, yes_link, no_link)

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
            data = data['response']['result'][module_name]['row']['FL']
            return data
        except ValueError, Argument:
            print "Incorrect json response structure from zoho API", Argument

    def extract_potential_data(self, potential_json):
        """
        extract the potential data we need for our models
        """
        potential_to_installation = {
                'POTENTIALID':'potential_id',
                'Potential Name':'potential_name',
                'Site Street':'site_address',
                'Site Street 2':'site_address_two',
                'Site Post Code':'site_postcode',
                'CONTACTID':'contact_id'}

        p_data = {}
        for set in potential_json:
            value = set['val']
            content = set['content']
            for pot, ins in potential_to_installation.iteritems():
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
    def get(self, request, *args, **kwargs):
        installation_id = self.kwargs.get('installation_id')
        installation = Installation.objects.get(id=installation_id)
        answer = request.GET.get('confirm')
        if answer == 'yes':
            installation.contractor_confirmed = True
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
            return HttpResponseRedirect(reverse('installation-detail', kwargs={'pk': installation_id}))
    else:
        form = ContractorForm()
    return render(
            request,
            'installations/installation_dates.html',
            {'form': form,
            'installation_id': installation_id})
