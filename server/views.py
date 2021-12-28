from django.shortcuts import render

##TEMPLATES
LOGIN_TEMPLATE = "login.html"


# Create your views here.
def login(request):
    return render(request, LOGIN_TEMPLATE)
