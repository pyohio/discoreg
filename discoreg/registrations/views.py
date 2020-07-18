import os


from django.urls import resolve
from django.http import HttpResponse
from django.shortcuts import redirect
from requests_oauthlib import OAuth2Session

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
    "connections",
]

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
    return HttpResponse("Registration!")


def callback(request):
    if request.GET.get("error"):
        return HttpResponse(request.GET.get("error"))

    discord_session = make_session(state=request.GET["state"],)
    token = discord_session.fetch_token(
        DISCORD_TOKEN_URL,
        client_secret=DISCORD_CLIENT_SECRET,
        code=request.GET["code"],
        authorization_response=f"https://tylerdave.ngrok.com/{request.get_full_path()}",
    )
    auth_session = make_session(token=token)
    user = auth_session.get(f"{DISCORD_API_BASE_URL}/users/@me").json()

    return HttpResponse(f"Linked: {user}")


def link(request):
    discord_session = make_session()
    authorization_url, state = discord_session.authorization_url(
        DISCORD_AUTHORIZATION_BASE_URL
    )
    return redirect(authorization_url)
    return HttpResponse(authorization_url)
