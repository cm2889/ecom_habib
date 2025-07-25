from django.template.response import TemplateResponse
from django.shortcuts import render

from backend.models import FrontendDesignSettings


def dynamic_css(request):
    return TemplateResponse(request, "css/dynamic_styles.css", content_type="text/css")


def homepage(request):
    return render(request, "homepage.html")
