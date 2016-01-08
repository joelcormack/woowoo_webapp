from django.conf import settings
import urllib
import urllib2
import json

class Zoho:
    def __init__(self, authtoken=settings.ZOHO_AUTHTOKEN):
        self.authtoken = authtoken

    def get_record_data(self, module_name, record_id):
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
                'Site Post Code':'site_postcode',
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
                'Phone' : 'phone',
                'Email': 'email'}

    def extract_potential_data(self, potential_json):
        """extract the potential data we need for our models"""
        p_data = {}
        for set in potential_json:
            value = set['val']
            content = set['content']
            for pot, ins in self.potential_to_installation.iteritems():
                if value == pot:
                    p_data[ins] = content

        return p_data

    def extract_product_data(self, product):
        """extract the product data"""
        products = {}
        for set in product:
            value = set['val']
            content = set['content']
            for pot, ins in self.product.iteritems():
                if value == pot:
                    products[ins] = content

        return products

    def extract_contact_data(self, contact_json):
        """
        extract the potential data we need for our models
        """
        c_data = {}
        for set in contact_json:
            value = set['val']
            content = set['content']
            for contact_zoho, contact in self.contact_zoho_to_contact.iteritems():
                if value == contact_zoho:
                    c_data[contact] = content

        return c_data

