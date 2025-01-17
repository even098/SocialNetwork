import google_auth_oauthlib
from attrs import define
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.urls import reverse_lazy

import google_auth_oauthlib.flow
import requests
import jwt
from django.utils.text import slugify
from rest_framework.exceptions import AuthenticationFailed


UserModel = get_user_model()


@define
class GoogleSdkLoginCredentials:
    client_id: str
    client_secret: str
    project_id: str


@define
class GoogleAccessTokens:
    id_token: str
    access_token: str

    def decode_id_token(self):
        id_token = self.id_token
        decoded_token = jwt.decode(jwt=id_token, options={"verify_signature": False})
        return decoded_token


def google_sdk_login_get_credentials() -> GoogleSdkLoginCredentials:
    client_id = settings.GOOGLE_OAUTH2_CLIENT_ID
    client_secret = settings.GOOGLE_OAUTH2_CLIENT_SECRET
    project_id = settings.GOOGLE_OAUTH2_PROJECT_ID

    if not client_id:
        raise ImproperlyConfigured("GOOGLE_OAUTH2_CLIENT_ID missing in env.")

    if not client_secret:
        raise ImproperlyConfigured("GOOGLE_OAUTH2_CLIENT_SECRET missing in env.")

    if not project_id:
        raise ImproperlyConfigured("GOOGLE_OAUTH2_PROJECT_ID missing in env.")

    credentials = GoogleSdkLoginCredentials(
        client_id=client_id,
        client_secret=client_secret,
        project_id=project_id
    )

    return credentials


class GoogleSdkLoginFlowService:
    API_URI = reverse_lazy("callback-sdk")

    # Two options are available: 'web', 'installed'
    GOOGLE_CLIENT_TYPE = "web"

    GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
    GOOGLE_ACCESS_TOKEN_OBTAIN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
    GOOGLE_USER_ADDITIONAL_INFO_URL = "https://people.googleapis.com/v1/people/me"

    # Add auth_provider_x509_cert_url if you want verification on JWTS such as ID tokens
    GOOGLE_AUTH_PROVIDER_CERT_URL = ""

    SCOPES = [
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/user.birthday.read",
        "https://www.googleapis.com/auth/user.gender.read",
        "openid",
    ]

    def __init__(self):
        self._credentials = google_sdk_login_get_credentials()

    def _get_redirect_uri(self):
        domain = settings.BASE_BACKEND_URL
        api_uri = self.API_URI
        redirect_uri = f"{domain}{api_uri}"
        return redirect_uri

    def _generate_client_config(self):
        # This follows the structure of the official "client_secret.json" file
        client_config = {
            self.GOOGLE_CLIENT_TYPE: {
                "client_id": self._credentials.client_id,
                "project_id": self._credentials.project_id,
                "auth_uri": self.GOOGLE_AUTH_URL,
                "token_uri": self.GOOGLE_ACCESS_TOKEN_OBTAIN_URL,
                "auth_provider_x509_cert_url": self.GOOGLE_AUTH_PROVIDER_CERT_URL,
                "client_secret": self._credentials.client_secret,
                "redirect_uris": [self._get_redirect_uri()],
                # If you are dealing with single page applications,
                # you'll need to set this both in Google API console
                # and here.
                "javascript_origins": [],
            }
        }
        return client_config

    def get_user_info(self, *, google_tokens: GoogleAccessTokens):
        access_token = google_tokens.access_token
        response = requests.get(
            self.GOOGLE_USER_INFO_URL,
            params={"access_token": access_token}
        )

        # if additional_info.status_code == 200:
        #     add_info = additional_info.json()
        #     print(add_info)

        if not response.ok:
            raise AuthenticationFailed("Failed to obtain user info from Google.")

        user_info = response.json()
        email = user_info.get("email")

        try:
            user = UserModel.objects.get(email=email)
        except ObjectDoesNotExist:
            response = requests.get(
                self.GOOGLE_USER_ADDITIONAL_INFO_URL,
                params={"access_token": access_token, "personFields": "genders,birthdays"}
            )
            additional_info = response.json()

            gender = additional_info.get('genders', [{}])[0].get('value', 'other')
            birthday_data = additional_info.get('birthdays', [{}])[0].get('date', {})
            year = birthday_data.get('year', None)
            month = birthday_data.get('month', None)
            day = birthday_data.get('day', None)

            username_base = slugify(user_info.get("name", "user"))
            username = username_base

            counter = 1
            while UserModel.objects.filter(username=username).exists():
                username = f"{username_base}_{counter}"
                counter += 1

            birthday = f"{year}-{month:02d}-{day:02d}" if year and month and day else None

            user = UserModel.objects.create(
                username=username,
                full_name=user_info.get('name'),
                avatar=user_info.get('picture'),
                date_of_birth=birthday,
                gender=gender,
                email=email,
            )
        return user_info

    def get_tokens(self, *, code: str, state: str) -> GoogleAccessTokens:
        redirect_uri = self._get_redirect_uri()
        client_config = self._generate_client_config()

        flow = google_auth_oauthlib.flow.Flow.from_client_config(
            client_config=client_config, scopes=self.SCOPES, state=state
        )
        flow.redirect_uri = redirect_uri
        access_credentials_payload = flow.fetch_token(code=code)

        if not access_credentials_payload:
            raise AuthenticationFailed("Failed to obtain tokens from Google.")

        google_tokens = GoogleAccessTokens(
            id_token=access_credentials_payload["id_token"],
            access_token=access_credentials_payload["access_token"]
        )
        user_info = self.get_user_info(google_tokens=google_tokens)

        return google_tokens

    def get_authorization_url(self):
        redirect_uri = self._get_redirect_uri()
        client_config = self._generate_client_config()

        google_oauth_flow = google_auth_oauthlib.flow.Flow.from_client_config(
            client_config=client_config, scopes=self.SCOPES
        )
        google_oauth_flow.redirect_uri = redirect_uri

        authorization_url, state = google_oauth_flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="select_account",
        )
        return authorization_url, state
