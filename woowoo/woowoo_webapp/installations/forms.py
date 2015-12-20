from django import forms
from datetime import date

class ContractorForm(forms.Form):
    installation_date = forms.DateField(label='Installation Date')
    delivery_date = forms.DateField(label='Delivery Date')
