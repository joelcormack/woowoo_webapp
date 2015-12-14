from django.shortcuts import render
from django.views.generic import View, ListView, DetailView
from .models import Installation
  
class InstallationList(ListView):
    model = Installation

class InstallationDetail(DetailView):
    model = Installation

class CreateInstallation(View):
    pass 

# Create your views here.
