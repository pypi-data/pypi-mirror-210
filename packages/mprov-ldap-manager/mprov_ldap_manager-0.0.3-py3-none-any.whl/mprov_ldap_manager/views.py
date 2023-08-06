# Mainly used if there are API endpoints for this mProv module

from django.http import HttpResponse
from common.views import MProvView
import platform
from django.shortcuts import render
from django.template.response import TemplateResponse


