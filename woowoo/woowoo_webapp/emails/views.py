from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


def send_provisional_date(date, yes, no):
    msg_html = render_to_string('emails/provisional_date_notifier.html', {
        'recipient': 'Jake',
        'yes' : yes,
        'no': no,
        'date' : date})
    send_mail('Please confirm this provisional date',
        'bill',
        settings.APPLICATION_EMAIL,
        [settings.CONTRACTOR_EMAIL],
        fail_silently=False,
	html_message=msg_html)

def send_installation_and_delivery_form(answer, date,  name, number, email, form):
    if answer == 'yes':
        msg_html = render_to_string('emails/installation_and_delivery_form_notifier.html', {
            'recipient': 'Jake',
            'date': date,
            'customer_name': name,
            'number':number,
            'email': email,
            'form': form})
    else:
        msg_html = render_to_string('emails/installation_and_delivery_form_notifier_answer_no.html', {
            'recipient': 'Jake',
            'date': date,
            'customer_name': name,
            'number':number,
            'email': email,
            'form': form})

    send_mail('Installation and Delivery Date Form',
        'bill',
        settings.APPLICATION_EMAIL,
        [settings.CONTRACTOR_EMAIL],
        fail_silently=False,
        html_message=msg_html)

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
                settings.APPLICATION_EMAIL,
                [settings.MANAGER_EMAIL, settings.CONTRACTOR_EMAIL],
                fail_silently=False)

def send_kazuba_pickup_date(links):
    body="""
Hello Kazuba,

Installation and delivery dates have been confirmed with customer and contractor and a purchase order has been sent to you. Please see details below and confirm the the pickup date.

Name of site: %s
Pikup Date: %s


Is the pickup date good for you?

<a href="%s">yes</a>
<a href="%s">no</a>

Thanks,

Woo Woo Web App
""" % links
    send_mail('Installation and Delivery Confirmation',
                body,
                settings.APPLICATION_EMAIL,
                [settings.MANAGER_EMAIL, settings.CONTRACTOR_EMAIL],
                fail_silently=False)

def send_final_confirmation(links):
    body="""
Hello James, customer and contractor,

Installation and delivery dates below have been booked and conrimed. If these are wrong please get in contact otherwise you can view the status of the order here....

Name of site: %s
Pikup Date: %s
Delivery Date: %s
Installation Date: %s

Thanks,

Woo Woo Web App
""" % links
    send_mail('Installation and Delivery Confirmation',
                body,
                settings.APPLICATION_EMAIL,
                [settings.MANAGER_EMAIL, settings.CONTRACTOR_EMAIL, settings.CUSTOMER_EMAIL],
                fail_silently=False)
