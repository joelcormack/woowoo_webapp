from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

def send_installation_exists_notifier(recipient, installation, pid):
    msg_html = render_to_string('emails/installation_exists_notifier.html', {
        'recipient': recipient,
        'pid': pid,
        'installation' : installation})
    send_mail('Installation already exists',
        'bill',
        settings.APPLICATION_EMAIL,
        [settings.MANAGER_EMAIL],
        fail_silently=False,
	html_message=msg_html)


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

def send_confirmation_email(site_name, delivery_date, installation_date):
    msg_html = render_to_string('emails/customer_and_contractor_confirmation_notifier.html', {
        'recipient': 'James',
        'site_name': site_name,
        'delivery_date': delivery_date,
        'installation_date': installation_date})

    send_mail('Installation and Delivery Confirmation',
        'plain text here',
        settings.APPLICATION_EMAIL,
        [settings.MANAGER_EMAIL, settings.CONTRACTOR_EMAIL],
        fail_silently=False,
        html_message=msg_html)

def send_retailer_pickup_date(site_name, pickup_date, yes_link, no_link):
    msg_html = render_to_string('emails/retailer_pickup_date_notifier.html', {
        'recipient': 'Kazuba',
        'site_name': site_name,
        'pickup_date': pickup_date,
        'yes':yes_link,
        'no':no_link})

    send_mail('Installation and Delivery Confirmation',
                'plain_text',
                settings.APPLICATION_EMAIL,
                [settings.MANAGER_EMAIL, settings.CONTRACTOR_EMAIL],
                fail_silently=False,
                html_message=msg_html)

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
