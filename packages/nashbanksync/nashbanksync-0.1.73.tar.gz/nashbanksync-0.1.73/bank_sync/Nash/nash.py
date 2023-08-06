from pickle import GLOBAL
from bank_sync.Resources.banks import Bank
from bank_sync.Resources.resource import Resource


class Nash(Resource):

    _headers = {
        'Content-Type': 'application/json'
    }

    _params = {}

    _response = {}

    _is_logged_in = False

    _bank = None

    _access_token = None

    _user_id = -1

    def __init__(self, oauth2_client_id=None, client_secret=None, auth_scope=None):
        super().__init__("NashAPI", self._headers, self._params)
        # If auth credential are provided in the constructor go ahead and initiate a log in request
        if oauth2_client_id and client_secret and auth_scope:
            self.login(oauth2_client_id=oauth2_client_id,
                       client_secret=client_secret, auth_scope=auth_scope)

    def login(self, oauth2_client_id=None, client_secret=None, auth_scope=None):
        # authenticate and provide user credentials

        auth_token_url = super().BANKS_CONF.get(super().AUTHENTICATE, {}).get('url', '') + "/" \
            + super().BANKS_CONF.get(super().AUTHENTICATE, {}).get('read', {}
                                                                   ).get('operations', {}).get(super().AUTH_GET_TOKEN, '')[0]

        super().set_oauth2_client_id(oauth2_client_id=oauth2_client_id)\
            .set_client_secret(client_secret=client_secret)\
            .set_auth_token_url(auth_token_url=auth_token_url)\
            .set_auth_scope(auth_scope=auth_scope)\
            .fetch_identity_token()

        return self

    def sign_up(self, payload=None, method='POST', endpoint="/users", log_in_user=True):
        # authenticate and provide user credentials
        # set response here

        self.login(payload={"username": payload.get(
            "username"), "password": payload.get("password")}).response()

        return self

    def bank(self, bank_id=0):
        self._bank = Bank(self, bank_id).set_oauth2_client_id(oauth2_client_id=super().get_oauth2_client_id())\
                    .set_client_secret(client_secret=super().get_client_secret())\
                    .set_auth_token_url(auth_token_url=super().get_auth_token_url())\
                    .set_auth_scope(auth_scope=super().get_auth_scope())

        return self._bank

    # def user(self):
    #     return Users(self)

    def is_logged_in(self):
        return self._is_logged_in

    # def _set_access_token(self, access_token):
    #     self._access_token = access_token
    #     return self

    # def get_access_token(self):
    #     return self._access_token
