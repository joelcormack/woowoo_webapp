from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View, ListView, DetailView
from .models import Installation

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
        potential_id = request.GET.get('pid')
        authtoken = settings.ZOHO_AUTHTOKEN
        module_name = 'Potentials'
        params = {'authtoken':authtoken,'scope':'crmapi','criteria':'(Potential ID:'+potential_id+')'}
        final_URL = "https://crm.zoho.com/crm/private/json/"+module_name+"/searchRecords"
        data = urllib.urlencode(params)
        request = urllib2.Request(final_URL,data)
        response = urllib2.urlopen(request)
        json_response = response.read()
        data = json.loads(json_response)
        pretty_data = pprint.pformat(data)
        return HttpResponse(pretty_data)


