from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View, ListView, DetailView
from .models import Installation

class InstallationList(ListView):
    model = Installation

class InstallationDetail(DetailView):
    model = Installation

class CreateInstallation(View):
    def get(self, request):
        potential_id = request.GET.get('pid')

        return HttpResponse(potential_id)
