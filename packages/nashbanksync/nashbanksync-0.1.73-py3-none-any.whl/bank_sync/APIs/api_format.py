import json
import requests
from datetime import datetime, timezone, timedelta
from rest_framework import status
try:
    from django.conf import settings
except Exception as e:
    pass
# This is a class that is designed to include all methods and functions one needs to make an A.P.I. call

class API(object):

    _auth_token_url = None
    _oauth2_client_id = None
    _client_secret = None
    _identity_token = None
    _auth_scope = None
    _is_identity_config_set = False
    _error = False

    global_session = requests.Session()

    try:
        _oauth2_client_id = getattr(
            settings, 'OAUTH2_CLIENT_ID', _oauth2_client_id)
        _client_secret = getattr(
            settings, 'CLIENT_SECRET', _client_secret)
        _auth_token_url = getattr(
            settings, 'OAUTH2_TOKEN_URL', _auth_token_url)
        _auth_scope = getattr(
            settings, 'OAUTH2_SCOPE', _auth_scope)
    except Exception as e:
        pass

    _full_url = ""

    # Most API calls require headers, params and payloads
    _headers = None
    _params = None
    _payload = None

    # You always expect a response from A.P.I. calls
    _response = {}

    # You always expect a response code from A.P.I. calls
    _response_code = -1

    # When using this class to create an A.P.I. class, each API should have an optional name and code
    # but must have headers and any required parameters
    def __init__(self, name=None, headers=None, params=None, code=None):
        self._name = name
        self._code = code

        self._headers = headers
        self._params = params

        requests.packages.urllib3.disable_warnings()

    def execute_get_identity_token(self):
        refresh_token = False
        # check if an Authorization header was set in the global token
        if self.global_session.headers.get('Authorization'):
            # check when it was set to expire which is set in '%Y:%m:%d %H:%M:%S %z'
            auth_expires_in = self.global_session.headers.get(
                'auth_expires_in')
            # convert the string '%Y:%m:%d %H:%M:%S %z' to time
            auth_expires_in = datetime.strptime(
                auth_expires_in, '%Y:%m:%d %H:%M:%S %z')
            # get the current time and add ten minutes to it, so that we refresh the token 5 minutes before its expiry
            current_time = datetime.now(timezone.utc) + timedelta(minutes=5)
            # if current time plus 5 minutes is more than when the auth needs to expire
            # refresh the token
            if current_time > auth_expires_in:
                # first set the Authorization to an empty string
                self.global_session.headers.update({'Authorization': ''})
                refresh_token = True
        # If the Authorization header was not set in the global token
        else:
            refresh_token = True

        return refresh_token

    def fetch_identity_token(self):
        try:
            if self.execute_get_identity_token():
                _payload = {
                    'grant_type': 'client_credentials',
                    'scope': self._auth_scope,
                    'client_id': self._oauth2_client_id,
                    'client_secret': self._client_secret
                }
                self._identity_token = requests.request(
                    "POST", self._auth_token_url, data=_payload)
                if self._identity_token.status_code == 200:
                    self.global_session.headers.update({
                        'Authorization': f"{self._identity_token.json().get('access_token',None)}",
                        'auth_expires_in': (datetime.now(timezone.utc) + timedelta(seconds=self._identity_token.json().get('expires_in', 0))).strftime("%Y:%m:%d %H:%M:%S %z")
                    })
                    print("Identity Log In Successful")
                else:
                    raise Exception(self._identity_token.text)
        except Exception as e:
            raise Exception(
                f'Failed to Authenticate the User: {str(e)} self._identity_token" {self._identity_token} self._identity_token.content" {self._identity_token.content}')

        return self

    # There are 3 types of API requests that most APIs use, POST, GET and PUT
    # This method will take the payload or data to be sent and send it to the required API url
    # using the desired method and returns the response
    def api_request(self, payload, method, verify=False, files=None):

        if payload == "null":
            self._payload = json.dumps({})
        else:
            self._payload = payload

        try:
            # Authenticate this service on the Nash Identity Server
            self.fetch_identity_token()

            if self._headers is not None and self.global_session.headers.get('Authorization'):
                self._headers.update({
                    'Authorization': f"Bearer {self.global_session.headers.get('Authorization')}"
                })
            print(f'api_request self._headers: {self._headers}')
            if method == 'POST':
                self._response = requests.post(self.get_full_url(), headers=self._headers, params=self._params,
                                               data=self._payload, json=self._payload, verify=verify, files=files)
            elif method == 'PUT':
                self._response = requests.put(self.get_full_url(), headers=self._headers, params=self._params,
                                              data=self._payload, json=self._payload, verify=verify)
            elif method == 'GET':
                self._response = requests.get(self.get_full_url(), headers=self._headers, params=self._params,
                                              data=self._payload, json=self._payload, verify=verify)
            elif method == 'DELETE':
                self._response = requests.delete(self.get_full_url(), headers=self._headers, params=self._params,
                                                 data=self._payload, json=self._payload, verify=verify)
            try:
                if self._response.status_code == status.HTTP_200_OK:
                    # If the URL we called returns a response
                    if len(self._response.text):
                        self._response = json.loads(self._response.text)
                    # If the url we called returned no response return the default response below which holds the status code
                    else:
                        self._response = {'code': self._response.status_code}
                else:
                    if status.is_server_error(self._response.status_code):
                        self._response = {
                            'error': f'Bank Core Server Error: HTTP Error Code {self._response.status_code}'}
                    elif status.is_client_error(self._response.status_code):
                        self._response = {
                            'error': f'Bank Sync Service Server Error: HTTP Error Code {self._response.status_code}: {self.get_full_url()}'}
            except ValueError as e:
                print(f'Bank Sync Error: {str(e)}')
                self._response = {'error': f'Bank Sync Error: {str(e)} : Response {self._response}'}

        except Exception as e:
            print(f'Exception: {str(e)}')
            self._response = {'error': f'Bank Sync Error: {str(e)}'}
        finally:
            return self._response

    # Method used to get the repsonse returned by an API instead of calling the API again
    def get_response(self):
        return self._response

    def set_headers(self, headers):
        self._headers = headers
        return self

    def get_headers(self):
        return self._headers

    def set_params(self, params):
        self._params = params
        return self

    def set_full_url(self, full_url):
        self._full_url = full_url
        return self

    def get_params(self):
        return self._params

    def get_full_url(self):
        return self._full_url

    def get_payload(self):
        return self._payload

    def get_response_code(self):
        return self._response_code

    def set_response_code(self, response_code):
        self._response_code = response_code
        return self

    def set_identity_token(self, identity_token):
        self._identity_token = identity_token
        return self

    def set_oauth2_client_id(self, oauth2_client_id):
        self._oauth2_client_id = oauth2_client_id
        return self

    def get_oauth2_client_id(self):
        return self._oauth2_client_id

    def set_client_secret(self, client_secret):
        self._client_secret = client_secret
        return self

    def get_client_secret(self):
        return self._client_secret

    def set_auth_token_url(self, auth_token_url):
        self._auth_token_url = auth_token_url
        return self

    def get_auth_token_url(self):
        return self._auth_token_url

    def set_auth_scope(self, auth_scope):
        self._auth_scope = auth_scope
        return self

    def set_error(self, error):
        self._response = {"error": error}
        return self

    def get_auth_scope(self):
        return self._auth_scope

    def is_identity_config_set(self):
        if self.get_oauth2_client_id() and self.get_client_secret() and self.get_auth_token_url() and self.get_auth_scope():
            return True
        else:
            return False

    @property
    def get_identity_token(self):
        return self._identity_token
