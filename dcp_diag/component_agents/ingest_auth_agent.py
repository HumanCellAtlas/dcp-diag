import requests


class IngestAuthAgent:
    def __init__(self,
                 url="https://danielvaughan.eu.auth0.com/oauth/token",
                 client_id="Zdsog4nDAnhQ99yiKwMQWAPc2qUDlR99",
                 client_secret="t-OAE-GQk_nZZtWn-QQezJxDsLXmU7VSzlAh9cKW5vb87i90qlXGTvVNAjfT9weF",
                 audience="http://localhost:8080",
                 grant_type="client_credentials"):
        """This class controls the authentication actions with Ingest Service, including retrieving the token,
            store the token and make authenticated headers. Note: The parameters and credentials here are
            meant to be hard coded, the authentication is purely for identifying a user it doesn't give any permissions.

        :param str url: The url to the Auth0 domain oauth endpoint.
        :param str client_id: The value of the Client ID field of the Non Interactive Client of Auth0.
        :param str client_secret: The value of the Client Secret field of the Non Interactive Client of Auth0.
        :param str audience: The value of the Identifier field of the Auth0 Management API.
        :param str grant_type: Denotes which OAuth 2.0 flow you want to run. e.g. client_credentials
        """
        self.url = url
        self.client_id = client_id
        self.client_secret = client_secret
        self.audience = audience
        self.grant_type = grant_type
        self.auth_token = self._get_auth_token()

    def _get_auth_token(self):
        """Request and get the access token for a trusted client from Auth0.

        :return dict auth_token: JSON response of the signed JWT (JSON Web Token), with when it expires (24h by
            default), the scopes granted, and the token type.
        """
        url = self.url
        headers = {
            "content-type": "application/json"
        }
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "audience": self.audience,
            "grant_type": self.grant_type
        }
        response = requests.post(url=url, headers=headers, json=payload)
        response.raise_for_status()
        auth_token = response.json()
        return auth_token

    def make_auth_header(self):
        """Make the authorization headers to communicate with endpoints which implement Auth0 authentication API.

        :return dict headers: A header with necessary token information to talk to Auth0 authentication required
            endpoints.
        """
        token_type = self.auth_token['token_type']
        access_token = self.auth_token['access_token']

        headers = {
            "Authorization": f"{token_type} {access_token}"
        }
        return headers
