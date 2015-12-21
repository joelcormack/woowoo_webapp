from django.core.mail import send_mail

def send_provisional_date(links):
    body="""
Hi Jake,

We've received an order. The provisional week for delivery is %s (6 weeks from now).

Please confirm this is a good week for you to install.

<a href="%s">YES</a>

<a hfre="%s">NO</a>

Thanks,

Woo Woo Web App
""" % links

    
    send_mail('Please confirm this provisional date',
                body,
                'auto@waterlesstoilet.co.uk',
                ['contractor@waterlesstoilets.co.uk'],
                fail_silently=False)

def send_installation_and_delivery_form(links):
    body="""
Hi Jake,

Thanks for confirming the installation week %s. Please contact the customer to arrange installation and confirm the dates of delivery and installation in the form linked below.

<a href="%s">Dates Form</a>

Thanks,

Woo Woo Web App
""" % links 

    send_mail('Installation and Delivery Date Form',
                body,
                'auto@waterlesstoilet.co.uk',
                ['contractor@waterlesstoilets.co.uk'],
                fail_silently=False)


