from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.conf import settings
from django.db import models
from django.conf import settings
from decimal import *
import re, urllib
from datetime import date, timedelta

from emails.views import send_provisional_date, \
send_installation_and_delivery_form, send_confirmation_email, \
send_supplier_pickup_date, send_installation_exists_notifier, \
send_all_dates_confirmation, send_manager_notification_email, \
send_confirmation_to_contact, send_final_confirmation

class InstallationManager(models.Manager):
    def create_installation(self, data):
        forklift = data.get('forklift', '')
        if forklift == 'true':
            forklift = True
        else:
            forklift = False
        installation = self.create(
                id=data.get('potential_id', ''),
                name=data.get('potential_name', ''),
                address_one=data.get('site_address', ''),
                address_two=data.get('site_address_two', ''),
                city=data.get('site_city', ''),
                county=data.get('site_county', ''),
                postcode=data.get('site_postcode', ''),
                forklift_available=forklift,
                installation_method=data.get('install_method', ''),
                gmaps_link=data.get('gmap_link', ''),
                long_and_lat=data.get('long_lat', ''))
        print "Added Installation: ", installation.name
        return installation

class Installation(models.Model):
    """
    Models an installation with a date set on creation, installation date,
    delivery date and pickup date, booleans to monitor stages of confirmations for
    contractor, shipping, customer and supplier and associated sites and contacts.
    """
    def set_pickup(self):
        #calc pickup date
        delivery = self.delivery_date.weekday()
        diff = 2 - delivery #2 is wednesday
        if delivery > 0 and delivery < 5:
            self.pickup_date = self.delivery_date - timedelta(days=7 - diff)
        else:
            self.pickup_date = self.delivery_date - timedelta(days=14 - diff)
        self.save()
        print self.pickup_date

    def get_provisional_date(self):
        """calculate provisional date"""
        def next_weekday(day, weekday):
            days_ahead = weekday - day.weekday()
            if days_ahead <= 0: # Target day already happened this week
                days_ahead += 7
            return day + timedelta(days_ahead)
        return next_weekday(self.created_date + timedelta(days=42), 0)

    SELF_INSTALL = 'SI'
    CONTRACTOR_INSTALL = 'CI'
    GGM_INSTALL = 'GG'
    SELF_AND_GGM = 'SG'
    INSTALLATION_METHODS = (
            (SELF_INSTALL, 'Self Install'),
            (CONTRACTOR_INSTALL, 'Contractor Install'),
            (GGM_INSTALL, 'GGM Install'),
            (SELF_AND_GGM, 'Self Install with GGM Assistance'))

    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=60)
    address_one = models.CharField(max_length=50)
    address_two = models.CharField(max_length=50, null=True)
    city = models.CharField(max_length=50, null=True)
    county = models.CharField(max_length=50, null=True)
    postcode = models.CharField(max_length=10)
    created_date = models.DateField(auto_now_add=True)
    forklift_available = models.BooleanField(default=False)
    installation_method = models.CharField(choices=INSTALLATION_METHODS, default=SELF_INSTALL, max_length=2)
    gmaps_link = models.URLField(null=True)
    long_and_lat = models.CharField(max_length=50, null=True)

    #unset on creation
    installation_date = models.DateField(null=True)
    delivery_date = models.DateField(null=True)
    pickup_date = models.DateField(null=True)
    contractor_confirmed = models.BooleanField(default=False)
    shipping_confirmed = models.BooleanField(default=False)
    shipping_receipt = models.FileField(upload_to='shipping_receipts/%Y/%m/%d', null=True)
    customer_confirmed = models.BooleanField(default=False)
    supplier_confirmed = models.BooleanField(default=False)
    objects = InstallationManager()

    def __unicode__(self):
        return self.name

    def get_status(self):
        """
        1 = customer and contractor need to confirm
        2 = supplier needs to confirm pickup date
        3 = shipping company needs to confirm dates
        4 = all dates confirmed
        """
        if self.customer_confirmed:
            if self.supplier_confirmed:
                if self.shipping_confirmed:
                    return "All dates have been confirmed and delivery is booked"
                else:
                    return "Shipping company needs to confirm loading and unloading dates"
            else:
                return "Supplier needs to confirm pickup date"
        else:
            return "Contractor needs to confirm dates with customer"

    def get_gmaps_url(self):
		try:
			params = urllib.urlencode({'q': self.long_and_lat.replace(" ",""),'key': settings.GOOGLE_MAPS_KEY})
			gmap_url = "https://www.google.com/maps/embed/v1/search?%s" % params
		except AttributeError:
			print "No Longitude and Latitude provided, using postcode for embedded Google map"""
			params = urllib.urlencode({'q': self.postcode.replace(" ",""),'key': settings.GOOGLE_MAPS_KEY})
		return "https://www.google.com/maps/embed/v1/search?%s"	% params

    base_url = settings.SITE_URL + 'installations/'

    def link(self, department, tail):
        return self.base_url + self.id + department + tail

    def send_provisional_date_notification(self):
        if not self.GGM_INSTALL == self.installation_method:
            send_provisional_date(installation=self, recipient=settings.MANAGER, email_to=settings.MANAGER_EMAIL)
        else:
            send_provisional_date(installation=self)
        print "Sending provisional date to contractor or manager"

    def send_date_form_notification(self, answer):
        send_installation_and_delivery_form(
                answer=answer,
                date=self.get_provisional_date(),
                site_name=self.name,
                name=self.contact_set.first().name,
                number=self.contact_set.first().phone,
                email=self.contact_set.first().email,
                form=self.link('/contractor/', 'form/'))
        print "Sending date form email to contractor"

    def send_confirmation_notification(self):
        send_confirmation_email(
            site_name=self.name,
            delivery_date=self.delivery_date,
            installation_date=self.installation_date)
        print "Sending confirmation email"

    def send_supplier_pickup_date_notification(self):
        send_supplier_pickup_date(
            site_name=self.name,
            pickup_date=self.pickup_date.strftime('%d/%m/%Y'),
            yes_link=self.link('/supplier/', '?confirm=yes'),
            no_link=self.link('/supplier/', '?confirm=no'))
        print "Sending pickup date email to supplier"

    def send_installation_exists_notifier(self):
        send_installation_exists_notifier(
                recipient=settings.MANAGER,
                installation=self.name,
                pid=self.id)
        print "Sending installation exists email"

    def send_all_dates_notification(self):
        send_all_dates_confirmation(self)
        print "Sending confirmation of all dates"

    def send_manager_notification(self):
        send_manager_notification_email(
                installation.name,
                installation.pickup_date)
        print "Sending email to manager"

    def send_confirmation_to_contact(self):
        send_confirmation_to_contact(self)
        print "Sending confirmation email to contact"


class ContactManager(models.Manager):

    def create_contact(self, data, installation):
        contact = self.create(
            id=data.get('contact_id',''),
            name=data.get('first_name', '')+" "+data.get('last_name', ''),
            phone=data.get('phone',''),
            email=data.get('email',''),
            installation=installation)
        print "added  %s to %s" % (contact.name, installation)
        return contact


class Contact(models.Model):
    """
    Models a contact of the site with a name, email and phone numbers
    """
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=60)
    phone = models.CharField(max_length=40)
    #foreign key
    installation = models.ForeignKey(Installation, on_delete=models.CASCADE)
    objects = ContactManager()

    def __unicode__(self):
        return self.name

class ProductManager(models.Manager):
    def create_product(self, products, installation):
        for item in products.items():
            if int(item[1]) > 0:
                product = self.create(
                    name=item[0],
                    quantity=item[1],
                    installation=installation)
                print "added product %s to %s" % (product.name, installation)
                return product

class Product(models.Model):
    """
    Models a woo woo product, cabin or a loo with a given quantity
    """
    def get_rate(self):
        prices = {
                'KL1': Decimal(settings.PRICE_KL1),
                'KL2 prm': Decimal(settings.PRICE_KL2),
                'KL3': Decimal(settings.PRICE_KL3),
                'KLu': Decimal(settings.PRICE_KLU),
                'STK': Decimal(settings.PRICE_STK),
                }
        return prices.get(self.name, Decimal(0))


    PRODUCT_TYPES = (
            ('K1', 'KL1'),
            ('K2', 'KL2 prm'),
            ('K3', 'KL3'),
            ('Ku', 'KLu'),
            ('ST', 'STK'))

    name = models.CharField(choices=PRODUCT_TYPES, max_length=20, null=True)
    quantity = models.IntegerField(default=0, null=True)
    #foreign key
    installation = models.ForeignKey(Installation, on_delete=models.CASCADE)
    objects = ProductManager()

    def __unicode__(self):
        return self.name

from django_mailbox.signals import message_received
from django.dispatch import receiver
from installations.pdf_date_extractor import extract_dates
@receiver(message_received)
def match_receipt(sender, message, **args):
    """
    extract dates from attached reciept to match an exsiting
    installation as confirmation from shipping
    """
    print "message received in webapp"
    if message.attachments.count() > 0:
        if file_is_pdf(message.attachments.first()):
            dates = extract_dates(message)
            print "dates returned = " , dates
            match_dates(message,dates)

def match_dates(message,dates):
    installations = Installation.objects.filter(
                contractor_confirmed=True
            ).filter(
                shipping_confirmed=False)
    for installation in installations:
        if installation.pickup_date.strftime("%d/%m/%Y") == dates[0]:
            print "matched installation date"
            if installation.delivery_date.strftime("%d/%m/%Y") == dates[1]:
                print "matched delivery date"
                attachment = message.attachments.first()
                installation.shipping_receipt = attachment.document.url
                installation.shipping_confirmed = True
                installation.save()
                print "saved shipping receipt for %s, shipping_confirmed = %s, hauiler_receipt = %s" % (
                        installation,
                        installation.shipping_confirmed,
                        installation.shipping_receipt)
                send_final_confirmation(installation)


def file_is_pdf(filename):
    if re.search('\.pdf$', filename.get_filename()):
        return True
    else:
        print "File is not a pdf"
        return False


    print "I just recieved a message titled %s from a mailbox named %s" % (message.subject, message.mailbox.name, )
