from django.conf import settings
import urllib
import urllib2
import json

class Zoho:
    def __init__(self, authtoken=settings.ZOHO_AUTHTOKEN):
        self.authtoken = authtoken

    def get_potential_by_search(self, search_value):
        params = {'authtoken': self.authtoken,
                'scope':'crmapi',
                'selectColumns': 'Potentials(Potential Name,)',
                'searchColumn': 'potentialname',
                'searchValue': search_value}
        final_URL = "https://crm.zoho.com/crm/private/json/Potentials/getSearchRecordsByPDC"
        data = urllib.urlencode(params)
        request = urllib2.Request(final_URL,data)
        response = urllib2.urlopen(request)
        json_response = response.read()
        data = json.loads(json_response)
        try:
            data = data['response']['result']['Potentials']['row']['FL']
            return data
        except ValueError, Argument:
            print "Incorrect json response structure from zoho API", Argument


    def get_record(self, module_name, record_id):
        """
        retrieves potential data in json format
        from zoho api and returns a python dictionary
        """
        params = {'authtoken':self.authtoken,'scope':'crmapi','id':record_id}
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

    """ZOHO CRM maped --> app variables"""
    potential_to_installation = {
                'POTENTIALID':'potential_id',
                'Potential Name':'potential_name',
                'Site Street':'site_address',
                'Site Street 2':'site_address_two',
                'Site City':'site_city',
                'Site County':'site_county',
                'Site Post Code':'site_postcode',
                'Installation Method':'install_method',
                'Google Maps Link':'gmap_link',
                'Forklift Available':'forklift',
                'Installation Location (51.634759, -0.179661)':'long_lat',
                'CONTACTID':'contact_id'}
    product = { 'KL1':'KL1',
                'KL2 prm':'KL2 prm',
                'KL3':'KL3',
                'STK':'STK',
                'KLu':'KLu'}
    contact_zoho_to_contact = {
                'CONTACTID' : 'contact_id',
                'First Name': 'first_name',
                'Last Name': 'last_name',
                'Phone (main)' : 'phone',
                'Email': 'email'}

    def extract(self, data):
        """extract key and value pairs"""
        extracted_data = {}
        for set in data:
            value = set['val']
            content = set['content']
            for item, ins in self.data.iteritems():
                if value == pot:
                    extracted_data[ins] = content
        return extracted_data
