import os

import requests
from django.core.exceptions import ObjectDoesNotExist
from django.urls import resolve, reverse
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import redirect, render
from oauthlib.oauth2.rfc6749.errors import InvalidClientIdError
from requests_oauthlib import OAuth2Session

from ..models import EmailRole
from .tito import tito_webhook


DISCORD_API_BASE_URL = settings.DISCORD_API_BASE_URL
DISCORD_AUTHORIZATION_BASE_URL = settings.DISCORD_AUTHORIZATION_BASE_URL
DISCORD_BOT_TOKEN = settings.DISCORD_BOT_TOKEN
DISCORD_CLIENT_ID = settings.DISCORD_CLIENT_ID
DISCORD_CLIENT_SECRET = settings.DISCORD_CLIENT_SECRET
DISCORD_GUILD_ID = settings.DISCORD_GUILD_ID
DISCORD_SCOPES = settings.DISCORD_SCOPES
DISCORD_TOKEN_URL = settings.DISCORD_TOKEN_URL


def make_callback_uri(request):
    # FIXME: this is a hack! Need to figure out how to make sure this is a secure URI
    return request.build_absolute_uri(reverse("registrations:callback")).replace(
        "http://", "https://"
    )


def make_session(redirect_uri, token=None, state=None, scope=None):
    if scope is None:
        scope = DISCORD_SCOPES
    return OAuth2Session(
        client_id=DISCORD_CLIENT_ID,
        token=token,
        state=state,
        scope=scope,
        redirect_uri=redirect_uri,
        auto_refresh_kwargs={
            "client_id": DISCORD_CLIENT_ID,
            "client_secret": DISCORD_CLIENT_SECRET,
        },
        auto_refresh_url=DISCORD_TOKEN_URL,
    )


def render_error_response(request, error_title=None, error_message=None, status=400):
    if error_message is None:
        error_message = "There was an error verifying your account."
    context = {
        "error_title": error_title,
        "error_message": error_message,
    }
    return render(request, "registrations/error.html", context=context, status=status)


def get_user(auth_session):
    return auth_session.get(f"{DISCORD_API_BASE_URL}/users/@me").json()


def add_user_to_guild(user_id, token):
    auth_headers = {
        "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
    }
    url = f"{DISCORD_API_BASE_URL}/guilds/{DISCORD_GUILD_ID}/members/{user_id}"
    response = requests.put(
        url, json={"access_token": token["access_token"]}, headers=auth_headers
    )
    response.raise_for_status()
    return response


def add_user_to_role(user_id, role_id):
    auth_headers = {
        "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
    }
    url = f"{DISCORD_API_BASE_URL}/guilds/{DISCORD_GUILD_ID}/members/{user_id}/roles/{role_id}"
    response = requests.put(url, headers=auth_headers, json={})
    response.raise_for_status()
    return response


def index(request):
    return render(request, "registrations/index.html")


def callback(request):
    if request.GET.get("error"):
        return render_error_response(
            request,
            error_title=request.GET.get("error"),
            error_message=request.GET.get("error_description"),
            status=401,
        )

    callback_uri = make_callback_uri(request)

    discord_session = make_session(callback_uri, state=request.GET.get("state"))
    try:
        token = discord_session.fetch_token(
            DISCORD_TOKEN_URL,
            client_secret=DISCORD_CLIENT_SECRET,
            code=request.GET["code"],
            authorization_response=f"https://tylerdave.ngrok.com/{request.get_full_path()}",
        )
    except InvalidClientIdError:
        return render_error_response(
            request, error_message="Authorization invalid or expired."
        )
    except:
        return render_error_response(request)

    auth_session = make_session(callback_uri, token=token)

    user = get_user(auth_session)

    try:
        email_roles = EmailRole.objects.get(email__iexact=user["email"])
    except ObjectDoesNotExist:
        return render_error_response(
            request,
            error_title="Email Not Registered",
            error_message=f"A registration could not be found using your Discord account email address: {user['email']}. Please register for PyOhio using that email address or log in with another Discord account and then return to this site.",
        )

    add_user_to_guild(user["id"], token)

    # guilds = auth_session.get(f"{DISCORD_API_BASE_URL}/users/@me/guilds").json()

    # joined = auth_session.put(f"{DISCORD_API_BASE_URL}/guilds/{DISCORD_GUILD_ID}/members/{user['id']}").json()
    # roles = auth_session.get(f"{DISCORD_API_BASE_URL}/guilds/{DISCORD_GUILD_ID}/roles").json()
    # guilds2 = None #auth_session.get(f"{DISCORD_API_BASE_URL}/users/@me/guilds").json()
    # = discord_session.get(f"{DISCORD_API_BASE_URL}/users/@me").json()
    #
    added_roles = []
    for discord_role in email_roles.discord_roles.all():
        add_user_to_role(user["id"], discord_role.discord_role_id)
        added_roles.append(discord_role.name)

    # app_url = f"{DISCORD_API_BASE_URL}/applications/@me"
    # app_response = requests.get(app_url, headers=auth_headers)

    details = {
        # "token": token,
        # "access_token": token["access_token"],
        # "user_id": user["id"],
        # "join_url": join_url,
        # "request_headers": joined_response.request.headers,
        # "request_body": joined_response.request.body,
        # "roles": roles,
        # "role_data": role_data,
        # "role_url": role_response.request.url,
        # "role_response": role_response,
        # "user_res_data": user_response.json(),
        # "app_response": app_response.json(),
    }
    # details= None

    context = {
        "joined_username": user["username"],
        "joined_email": user["email"],
        "added_roles": added_roles,
    }
    return render(request, "registrations/success.html", context)


def link(request):
    callback_uri = make_callback_uri(request)
    discord_session = make_session(callback_uri)
    authorization_url, state = discord_session.authorization_url(
        DISCORD_AUTHORIZATION_BASE_URL
    )
    return redirect(authorization_url)
    return HttpResponse(authorization_url)
