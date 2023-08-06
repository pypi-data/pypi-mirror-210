""" Functions for interact with gcp secretmanager """

from google.cloud import secretmanager
from google.oauth2 import id_token
from google.auth.transport.requests import Request
from google.oauth2 import service_account


def get_secret(secret_id):
    client = secretmanager.SecretManagerServiceClient()
    secret = client.access_secret_version(request={"name": secret_id})
    value = secret.payload.data.decode("UTF-8")
    return value


def get_OIDC_token_iap_request(client_id, **kwargs):
    """Makes a request to an application protected by Identity-Aware Proxy."""

    # Set the default timeout, if missing
    if 'timeout' not in kwargs:
        kwargs['timeout'] = 90

    # Obtain an OpenID Connect (OIDC) token from metadata server or using service
    # account.
    open_id_connect_token = id_token.fetch_id_token(Request(), client_id)

    return open_id_connect_token


def get_workspace_impersonate_credentials_sa(credentials_info, scopes, impersonate_mail):

    credentials = service_account.Credentials.from_service_account_info(
        credentials_info)

    scoped_credentials = credentials.with_scopes(scopes)

    impersonate_credentials = scoped_credentials.with_subject(impersonate_mail)

    return impersonate_credentials
