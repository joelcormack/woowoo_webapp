"""woowoo_webapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url, include
from . import views
from .views import InstallationList, InstallationDetail, \
CreateInstallation, ContractorConfirmation, SupplierConfirmation

urlpatterns = [
    url(r'^$', InstallationList.as_view(), name='installation-list'),
    url(r'^(?P<pk>[\d]+)/$', InstallationDetail.as_view(), name='installation-detail'),
    url(r'^(?P<installation_id>[\d]+)/contractor/$', ContractorConfirmation.as_view(), name='contractor-confirmation'),
    url(r'^(?P<installation_id>[\d]+)/contractor/form/$', views.set_dates,  name='contractor-dates'),
    url(r'^(?P<installation_id>[\d]+)/supplier/$', SupplierConfirmation.as_view(), name='supplier-confirmation'),
    url(r'^(?P<installation_id>[\d]+)/supplier/form/$', views.set_dates,  name='supplier-dates'),
    url(r'^(?P<installation_id>[\d]+)/notify-contact/$', views.notify_contact,  name='notify-contact'),
    url(r'^add/', CreateInstallation.as_view()),
]
