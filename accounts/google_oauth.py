
import secrets
from urllib.parse import urlencode

from django.conf import settings
from django.core import signing


STATE_SALT = "google-oauth-state"


def create_oauth_state():

    nonce = secrets.token_urlsafe(32)

    state = signing.dumps(
        {"nonce": nonce},
        salt=STATE_SALT
    )

    return state, nonce


def build_google_authorization_url(state, nonce):

    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "nonce": nonce,
        "access_type": "online",
        "prompt": "select_account",
    }

    return (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        + urlencode(params)
    )
