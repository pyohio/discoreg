import json
import logging
import os

from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from ..models import DiscordRole, EmailRole, Registration


logger = logging.getLogger(__name__)

TITO_WEBHOOK_TOKEN = settings.TITO_WEBHOOK_TOKEN


@csrf_exempt
def tito_webhook(request):
    if request.META.get("HTTP_AUTHORIZATION") != f"Bearer {TITO_WEBHOOK_TOKEN}":
        return HttpResponse("Unauthorized", status=401)

    payload = json.loads(request.body.decode("utf-8"))
    logger.warning(payload)

    default_roles = DiscordRole.objects.filter(assign_by_default=True)

    email_role, created = EmailRole.objects.get_or_create(email=payload["email"])
    email_role.discord_roles.add(*default_roles)
    email_role.save()
    registration = Registration(email=email_role, reference_id=payload["reference_id"])
    registration.save()

    return HttpResponse(status=201)
