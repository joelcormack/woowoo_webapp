from __future__ import unicode_literals

from django.db import models

class Contact(models.Model):
    """
    Models a contact of the site with a name, email and phone numbers
    """
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=30)
    email = models.EmailField(max_length=30)
    phone = models.CharField(max_length=20)

    def __unicode__(self):
        return self.name


class Installation(models.Model):
    """
    Models an installation with a date set on creation, installation date,
    delivery date and pickup date, booleans to monitor stages of confirmations for
    contractot, haulier, customer and retailer and associated sites and contacts.
    """
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=30)
    address_one = models.CharField(max_length=50)
    address_two = models.CharField(max_length=50, null=True)
    postcode = models.CharField(max_length=10)
    created_date = models.DateField(auto_now_add=True)

    #unset on creation
    provisional_date = models.DateField(null=True)
    installation_date = models.DateField(null=True)
    delivery_date = models.DateField(null=True)
    pickup_date = models.DateField(null=True)
    contractor_confirmed = models.BooleanField(default=False)
    haulier_confirmed = models.BooleanField(default=False)
    customer_confirmed = models.BooleanField(default=False)
    retailer_confirmed = models.BooleanField(default=False)

    #foreign keys
    contacts = models.ForeignKey('Contact', on_delete=models.CASCADE)

    def __unicode__(self):
        return self.name
