import json
import logging
import os

from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)

TITO_WEBHOOK_TOKEN = settings.TITO_WEBHOOK_TOKEN

@csrf_exempt
def tito_webhook(request):
    if request.META.get('HTTP_AUTHORIZATION') != f"Bearer {TITO_WEBHOOK_TOKEN}":
        return HttpResponse("Unauthorized", status=401)

    payload = json.loads(request.body.decode("utf-8"))
    logger.warning(payload)
    return HttpResponse(status=201)