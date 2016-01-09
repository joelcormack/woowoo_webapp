from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View

class HomeView(View):
    html = "<html><body><h1>Woo Woo Web App</h1><p>Go to installations</p></body></html>" 
    def get(self, request):
        return HttpResponse(self.html)
