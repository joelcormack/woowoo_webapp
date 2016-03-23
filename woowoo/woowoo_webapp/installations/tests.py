from django.test import TestCase
from django.test import Client
from installations.models import Installation
from django.contrib.auth.models import User

class HomePageViewTest(TestCase):
    def test_index(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)

class InstallationListViewTest(TestCase):
    def test_unauthenticated_user(self):
        """
        unauthenticated users cannot access the installation
        list view and are redirected to login page
        """
        resp = self.client.get('/installations/')
        self.assertRedirects(resp, '/login/?next=/installations/')

    fixtures = ['fixtures.json']

    def test_authenticated_user(self):
        user = User.objects.get(username='django')
        self.client.force_login(user)
        resp = self.client.get('/installations/')
        self.assertEqual(resp.status_code, 200)

