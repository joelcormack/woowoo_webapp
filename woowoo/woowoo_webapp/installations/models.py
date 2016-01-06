from __future__ import unicode_literals

from django.db import models
import re

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
    haulier_receipt = models.FileField(upload_to='haulier_receipts/%Y/%m/%d', null=True)
    customer_confirmed = models.BooleanField(default=False)
    retailer_confirmed = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

class Contact(models.Model):
    """
    Models a contact of the site with a name, email and phone numbers
    """
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=30)
    email = models.EmailField(max_length=30)
    phone = models.CharField(max_length=20)
    #foreign key
    installation = models.ForeignKey(Installation, on_delete=models.CASCADE)
    def __unicode__(self):
        return self.name

class Product(models.Model):
    """
    Models a woo woo product, cabin or a loo with a given quantity
    """
    PRODUCT_TYPES = (
            ('K1', 'KL1'),
            ('K2', 'KL2 prm'),
            ('K3', 'KL3'),
            ('Ku', 'KL Urinal'),
            ('ST', 'STK'))
    name = models.CharField(choices=PRODUCT_TYPES, max_length=2, null=True)
    quantity = models.IntegerField(default=0, null=True)
    #foreign key
    installation = models.ForeignKey(Installation, on_delete=models.CASCADE)
    def __unicode__(self):
        return self.name


from django_mailbox.signals import message_received
from django.dispatch import receiver
from installations.pdf_date_extractor import extract_dates
@receiver(message_received)
def match_receipt(sender, message, **args):
    """
    extract dates from attached reciept to match an exsiting
    installation as confirmation from haulier
    """
    if file_is_pdf(message.attachments.first()):
        dates = extract_dates(message)
        print "dates returned = " , dates
        match_dates(message,dates)

def match_dates(message,dates):
    installations = Installation.objects.filter(
                contractor_confirmed=True
            ).filter(
                haulier_confirmed=False)
    for installation in installations:
        import ipdb; ipdb.set_trace()
        if installation.installation_date.strftime("%d/%m/%Y") == dates[0]:
            print "matched installation date"
            if installation.delivery_date.strftime("%d/%m/%Y") == dates[1]:
                print "matched delivery date"
                attachment = message.attachments.first()
                installation.haulier_receipt = attachment.document.url
                installation.haulier_confirmed = True
                installation.save()
                print "saved haulier receipt for %s, haulier_confirmed = %s, hauiler_receipt = %s" % (
                        installation,
                        installation.haulier_confirmed,
                        installation.haulier_receipt)

def file_is_pdf(filename):
    if re.search('\.pdf$', filename.get_filename()):
        return True
    else:
        print "File is not a pdf"
        return False


    print "I just recieved a message titled %s from a mailbox named %s" % (message.subject, message.mailbox.name, )
