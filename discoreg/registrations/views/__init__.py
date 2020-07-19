import os

import requests
from django.urls import resolve
from django.http import HttpResponse
from django.shortcuts import redirect, render
from requests_oauthlib import OAuth2Session

from .tito import tito_webhook

REDIRECT_URI = "https://tylerdave.ngrok.io/registrations/callback"
DISCORD_CLIENT_ID = os.environ["DISCORD_CLIENT_ID"]
DISCORD_CLIENT_SECRET = os.environ["DISCORD_CLIENT_SECRET"]
DISCORD_API_BASE_URL = "https://discord.com/api"
DISCORD_AUTHORIZATION_BASE_URL = f"{DISCORD_API_BASE_URL}/oauth2/authorize"
DISCORD_TOKEN_URL = f"{DISCORD_API_BASE_URL}/oauth2/token"
DISCORD_SCOPES = [
    "identify",
    "email",
    "guilds",
    "guilds.join",
    # "connections",
]
DISCORD_GUILD_ID = "715432774366003210"
DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]


# if 'http://' in REDIRECT_URI:
#     os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'


def make_session(token=None, state=None, scope=None):
    if scope is None:
        scope = DISCORD_SCOPES
    return OAuth2Session(
        client_id=DISCORD_CLIENT_ID,
        token=token,
        state=state,
        scope=scope,
        redirect_uri=REDIRECT_URI,
        auto_refresh_kwargs={
            "client_id": DISCORD_CLIENT_ID,
            "client_secret": DISCORD_CLIENT_SECRET,
        },
        auto_refresh_url=DISCORD_TOKEN_URL,
    )


def index(request):
    return HttpResponse(
        'Link your registration: <a href="/registrations/link">Link</a>'
    )


def callback(request):
    if request.GET.get("error"):
        return HttpResponse(request.GET.get("error"))

    discord_session = make_session(state=request.GET["state"])
    token = discord_session.fetch_token(
        DISCORD_TOKEN_URL,
        client_secret=DISCORD_CLIENT_SECRET,
        code=request.GET["code"],
        authorization_response=f"https://tylerdave.ngrok.com/{request.get_full_path()}",
    )
    auth_session = make_session(token=token)
    user = auth_session.get(f"{DISCORD_API_BASE_URL}/users/@me").json()
    guilds = auth_session.get(f"{DISCORD_API_BASE_URL}/users/@me/guilds").json()
    
   # joined = auth_session.put(f"{DISCORD_API_BASE_URL}/guilds/{DISCORD_GUILD_ID}/members/{user['id']}").json()
    #roles = auth_session.get(f"{DISCORD_API_BASE_URL}/guilds/{DISCORD_GUILD_ID}/roles").json()
    auth_headers = {
        'Authorization': f"Bot {DISCORD_BOT_TOKEN}",
    }
    join_url = f"{DISCORD_API_BASE_URL}/guilds/{DISCORD_GUILD_ID}/members/{user['id']}"
    
    joined_response= requests.put(join_url, json={'access_token': token['access_token']}, headers=auth_headers)
    joined_data = joined_response.content
        #guilds2 = None #auth_session.get(f"{DISCORD_API_BASE_URL}/users/@me/guilds").json()
    # = discord_session.get(f"{DISCORD_API_BASE_URL}/users/@me").json()  
    # 
    roles = requests.get(f"{DISCORD_API_BASE_URL}/guilds/{DISCORD_GUILD_ID}/roles", headers=auth_headers).json()

    ATTENDEE_ROLE="731868513068646460"
    role_url = f"{DISCORD_API_BASE_URL}/guilds/{DISCORD_GUILD_ID}/members/{user['id']}/roles/{ATTENDEE_ROLE}"
    role_response= requests.put(role_url, headers=auth_headers, json={})

    role_data = role_response.content
    
    app_url = f"{DISCORD_API_BASE_URL}/applications/@me"
    app_response = requests.get(app_url, headers=auth_headers)



    details={
        # "token": token,
        # "access_token": token["access_token"],
        # "user_id": user["id"],
        # "join_url": join_url,
        # "request_headers": joined_response.request.headers,
        # "request_body": joined_response.request.body,
        # "roles": roles,
        "role_data": role_data,
        "role_url": role_response.request.url,
        "role_response": role_response,
        # "user_res_data": user_response.json(),
        # "app_response": app_response.json(),
    }
    # details= None
     
    context = {
        "user": user,
        "email": user.get('email'),
        "servers": guilds,
        "joined": joined_data,
        "details": details,
    }
    return render(request, "registrations/link.html", context)

 
def link(request):
    discord_session = make_session()
    authorization_url, state = discord_session.authorization_url(
        DISCORD_AUTHORIZATION_BASE_URL
    )
    return redirect(authorization_url)
    return HttpResponse(authorization_url)

