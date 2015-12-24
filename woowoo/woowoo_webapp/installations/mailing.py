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

def send_installation_and_delivery_form(answer, links):
    if answer == 'yes':
        body="""
Hi Jake,

Thanks for confirming the installation week %s. Please contact the customer to arrange installation and confirm the dates of delivery and installation in the form linked below.

Custom name: %s
%s
<a href="mailto:%s">%s</a>

<a href="%s">Dates Form</a>

Thanks,

Woo Woo Web App
""" % links
    else:
        body="""
Hi Jake,

As the week beginning %s is not suitable, please contact the customer to arrange dates of delivery and installation and input them into the form linked below.

Custom name: %s
%s
<a href="mailto:%s">%s</a>

<a href="%s">Dates Form</a>

Thanks,

Woo Woo Web App
""" % links

    send_mail('Installation and Delivery Date Form',
                body,
                'auto@waterlesstoilet.co.uk',
                ['contractor@waterlesstoilets.co.uk'],
                fail_silently=False)

def send_confirmation_email(links):
    body="""
Hi,

Installation and delivery dates have been confirmed with customer and contractor for %s. Please see details below:

Name of site: %s
Delivery Date: %s
Installation Date: %s

Thanks,

Woo Woo Web App
""" % links
    send_mail('Installation and Delivery Confirmation',
                body,
                'auto@waterlesstoilet.co.uk',
                ['james@waterlesstoilets.co.uk', 'jake@waterlesstoilets.co.uk'],
                fail_silently=False)


