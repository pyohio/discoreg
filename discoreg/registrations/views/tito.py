from django.http import HttpResponse

def tito_webhook(request):
    return HttpResponse("Registration!")