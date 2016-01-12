# -*- coding: utf-8 -*-

from .settings import *

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


SECRET_KEY = '1fe7tyzfom8a$a52oa5_((k$@qd_)y!5oe_%6+*uu8pmmjimo2'

SITE_URL = 'http://localhost:8080/'

DEBUG = True

if DEBUG == True:
    #KF_SHIPPING_COMPANY_ID = KF_TEST_RECIPIENT_ID
    #KF_SHIPPING_COMPANY = KF_TEST_RECIPIENT_NAME
    #KF_SUPPLIER_ID = KF_TEST_RECIPIENT_ID
    #KF_SUPPLIER = KF_TEST_RECIPIENT_NAME
    SUPPLIER_EMAIL = 'joel@joelcormack.com'
    KF_SUPPLIER_EMAIL = SUPPLIER_EMAIL
    KF_SHIPPING_EMAIL_TO = "joel@joelcormack.com"



EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
