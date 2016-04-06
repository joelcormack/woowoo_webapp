from django.conf import settings
import requests
import json

class Zoho:
    def __init__(self, authtoken=settings.ZOHO_AUTHTOKEN):
        self.authtoken = authtoken

    def get_record(self, module_name, record_id):
        """
        retrieves potential data in json format
        from zoho api and returns a python dictionary
        """
        params = {'authtoken':'e1556f1fe39e4e34e0ff7feb1a213482',
                'scope':'crmapi',
                'id':record_id}
        final_URL = "https://crm.zoho.com/crm/private/json/" + module_name + "/getRecordById"
        r = requests.get(final_URL, params=params)
        data = r.json()
        try:
            data = data['response']['result'][module_name]['row']['FL']
            return data
        except ValueError, Argument:
            print "Incorrect json response structure from zoho API", Argument


    def extract(self, data, mapping):
        """extract key and value pairs"""
        extracted_data = {}
        for set in data:
            value = set['val']
            content = set['content']
            for item, ins in mapping.iteritems():
                if value == item:
                    extracted_data[ins] = content
        return extracted_data
