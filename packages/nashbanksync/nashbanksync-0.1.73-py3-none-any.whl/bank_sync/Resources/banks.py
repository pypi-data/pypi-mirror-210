from bank_sync.Resources.resource import Resource
from bank_sync.Resources.accounts import Accounts
from bank_sync.Resources.payments import Payments
from django.core.exceptions import ObjectDoesNotExist
from bank_sync.Resources.helpers import IsDjangoAppClass
from rest_framework import status

_is_django_app = False
try:
    from bank_sync.models import IPN
    from django.conf import settings
    _is_django_app = True
except Exception as e:
    _is_django_app = False

# This class is used as a patch, where incase we get an internal error while handling IPN
# We can paste that error here and return it gracefully as a response
class IPNErrorResponse():

    def __init__(self,error) -> None:
        self.error=error
    
    def response(self):
        return {"error":self.error}

class Bank(Resource):

    _resources = {
        "Accounts": Accounts(),
        "Payments": Payments(),
    }

    # use the nash object to confirm if the user accessing the banks is logged in
    _nash = None

    urls = {}

    # By default the library will set a url to use for ipn callbacks when registering an IPN
    bank_sync_ipn_urls = {}

    # This IPN callback is set in the django settings module
    # When a user registeres for an IPN using this service the sync will save the user url and forward the service url to Nash core
    # Nash will then forward ipn data to this service whihc then forwards it to the saved/registered user url
    if _is_django_app:
        bank_sync_ipn_urls = getattr(
            settings, 'BANK_SYNC_IPN_URLS', bank_sync_ipn_urls)

    def __init__(self, nash, bank_id=None):
        self._nash = nash
        super().__init__("BankAPI", self._nash.get_headers(), self._nash.get_params())
        super().set_bank_id(bank_id)

    def resource(self, resource_name):
        resource = self._resources[resource_name].set_bank_id(
            super().get_bank_id()).set_headers(self._nash.get_headers())\
            .set_oauth2_client_id(oauth2_client_id=super().get_oauth2_client_id())\
            .set_client_secret(client_secret=super().get_client_secret())\
            .set_auth_token_url(auth_token_url=super().get_auth_token_url())\
            .set_auth_scope(auth_scope=super().get_auth_scope())

        return resource

    def get_resources(self):
        return list(self._resources.keys())

    def callback(self, bank_name=None, payload=None, method='POST', endpoint='/callback'):

        if bank_name is not None:
            endpoint = f'{endpoint}/{bank_name}'

        return super().read(payload, method, endpoint)

    # This is a 'global' function
    # Used to get operations supported by Nash
    def bank_operations(self):
        return self.exec_global_function(operation=super().OPERATIONS)

    # This is a 'global' function
    # Used to get banks supported by Nash
    def bank_types(self):
        return self.bank_types_by_id()

    # This is a 'global' function
    # Used to get results of jobs that were scheduled
    def jobs(self, operation=None, payload=None):

        # The response returned is the raw response sent by banks before any standardizations
        rsp = self.exec_global_function(
            operation=operation, payload=payload).response()

        # The jobs that are currently being run are Account APIs get Account Balance and Account Full Statement API
        # For the above reason we will then initia.ize an Account Class that is responsible for standardizing Account APIs responses
        accounts = Accounts()
        # Set the bank id to identify the bank response being standardized
        accounts.set_bank_id(bank_id=rsp.get('bank_id'))
        # Set the operation to identify the bank api being standardized
        accounts.set_operation(operation=operation)
        # The set the response method is where the responses are standardized
        accounts.set_response(response=rsp)

        return accounts

    # This is a 'global' function used to:
    # 1. Register a user's I.P.N.'s in Nash
    # 2. Get a user's registered I.P.N.'s in Nash
    # 3. Update a user's registered I.P.N.'s in Nash
    # 4. Delete a user's registered I.P.N.'s in Nash

    # Here once an IPN is saved in Nash, we will create a replica DB that will also store, update or delete the IPN

    # We do this so that when an IPN is sent to us, we simply confirm if the if the IPN sent is coming from Nash
    # by comparing the security credentials and the account number sent at the endpoint responsible of standardizing
    # the response
    @IsDjangoAppClass(_is_django_app)
    def ipn(self, operation=None, payload=None):
        # Get the user passed url
        user_url = payload.get('url', '')

        # Get the user passed statement url
        statement_url = payload.get('statement_url', '')

        # if a user passed a url, swap it with the service's url
        if 'url' in payload.keys():
            payload['url'] = self.bank_sync_ipn_urls.get("payments", "")

        # if a user passed a statement_url, swap it with the service's statement url
        if 'statement_url' in payload.keys():
            payload['statement_url'] = self.bank_sync_ipn_urls.get("statement_url", "")

        exec_global = {}

        try:

            # For now we do not want a user to pass the client id and secret ID
            # so we will use the users account number to get the client id and signature
            if 'account_number' in payload.keys():
                if operation != super().IPN_REGISTER:
                    data = IPN.objects.get(
                        account_number=payload.get('account_number', ''))
                    payload['signature'] = data.signature
                    payload['client_id'] = data.client_id

            # excute the IPN call
            exec_global = self.exec_global_function(
                operation=operation, payload=payload)

            if operation in [super().IPN_REGISTER] and 'error' not in super().response().keys():
                # get the response and change the url saved, which it the service url, with the user url
                rsp = super().response()
                rsp['url'] = user_url
                super().set_response(response=rsp)

            # If the operation performed is to create an IPN
            if operation == super().IPN_REGISTER:
                # If succesfull Nash returns the generated client id and client secret
                if 'client_id' in super().response().keys() and 'client_secret' in super().response().keys():
                    signature = self.generate_signature(secret=super().response().get(
                        'client_secret'), message=f"{super().response().get('client_id')}:{super().response().get('client_secret')}")

                    IPN.objects.create(bank_id=payload.get('bank_id', ''), tenant_id=payload.get('tenant_id', None), business_id=payload.get('business_organization_unit_id', None), client_id=super().response().get(
                        'client_id', ''), signature=signature, country_code=payload.get('country_code', ''), currency_code=payload.get('currency_code', ''), account_number=payload.get('account_number', ''), 
                        url=user_url, statement_url=statement_url)

            # If the operation performed is to update an IPN
            elif operation == super().IPN_GET:
                # If succesfull Nash returns the client id and account_number
                if 'client_id' in super().response().keys() and 'account_number' in super().response().keys():

                    data = IPN.objects.get(client_id=super().response().get(
                        'client_id', ''), account_number=super().response().get('account_number', ''))

                    rsp = super().response()
                    rsp['bank_id'] = data.bank_id
                    rsp['tenant_id'] = data.tenant_id
                    rsp['business_organization_unit_id'] = data.business_id
                    rsp['url'] = data.url
                    rsp['statement_url'] = data.statement_url
                    super().set_response(response=rsp)

            # If the operation performed is to update an IPN
            elif operation == super().IPN_GENERATE_CLIENT_SECRET:
                # If succesfull Nash returns the client id
                if 'client_id' in super().response().keys():

                    data = IPN.objects.get(client_id=payload.get(
                        'client_id', ''), account_number=payload.get('account_number', ''))

                    if 'client_secret' in super().response().keys():
                        data.signature = self.generate_signature(secret=super().response().get(
                            'client_secret'), message=f"{super().response().get('client_id')}:{super().response().get('client_secret')}")

                    data.save()

            # If the operation performed is to update an IPN
            elif operation == super().IPN_UPDATE:
                # If succesfull Nash returns the client id
                if 'client_id' in super().response().keys():

                    data = IPN.objects.get(
                        client_id=payload.get('client_id', ''))

                    if 'bank_id' in payload.keys():
                        data.bank_id = payload.get('bank_id')
                    if 'country_code' in payload.keys():
                        data.country_code = payload.get('country_code')
                    if 'currency_code' in payload.keys():
                        data.currency_code = payload.get('currency_code')
                    if 'url' in payload.keys():
                        data.url = user_url
                    if 'statement_url' in payload.keys():
                        data.statement_url = statement_url
                    if 'status' in payload.keys():
                        data.status = payload.get('status')
                    if 'ipn_type' in payload.keys():
                        data.ipn_type = payload.get('ipn_type')
                    if 'tenant_id' in payload.keys():
                        data.tenant_id = payload.get('tenant_id')
                    if 'business_organization_unit_id' in payload.keys():
                        data.business_id = payload.get(
                            'business_organization_unit_id')

                    data.save()

            # If the operation performed is to delete an I.P.N.
            elif operation == super().IPN_DELETE:
                # If succesfull Nash returns the client id
                if 'client_id' in super().response().keys():

                    data = IPN.objects.get(client_id=payload.get(
                        'client_id', ''))

                    data.delete()

            # If the operation performed is to deactivate an I.P.N.
            elif operation == super().IPN_DEACTIVATE:
                # If succesfull Nash returns the client id
                if 'client_id' in super().response().keys():

                    data = IPN.objects.get(client_id=payload.get(
                        'client_id', ''))
                    data.status = False
                    data.save()

            # for now we do not want to return the client id and secret to the user
            # we will pop it from the response
            if 'client_id' in super().response().keys():
                super().response().pop('client_id')
            if 'client_secret' in super().response().keys():
                super().response().pop('client_secret')

        except ObjectDoesNotExist:
            exec_global=IPNErrorResponse(error="I.P.N. doesn't exist.")
            print(exec_global.response())

        except Exception as e:
            exec_global=IPNErrorResponse(error=f"Error: {str(e)}")
            print(exec_global.response())

        return exec_global

    # This method is used to standardize an Entity Operation, which is why it has been placed in the Super Entity Bank Class
    @IsDjangoAppClass(_is_django_app)
    def standardize_callback_statement(self, statement_data={}, forward=True):

        response = {
            "bank_id": statement_data.get("bank_id", -1),
            "account_number": statement_data.get("account_number", -1),
        }

        try:

            # Use the reference of the callback sent to get the callback data that was linked to the operation
            # This will returns a queryset, you will use .first() method or len() to manipultate it
            saved_ipn = IPN.objects.get(bank_id=statement_data.get("bank_id", ""), account_number=statement_data.get("account_number"))

            # set the bank id of the bank we have received the full statement data
            bank_ = self.set_bank_id(bank_id=statement_data.get("bank_id", -1))

            # set the operation we are want to standardize
            # set the full statement response we receive
            accounts_resource = bank_.resource("Accounts").set_operation(super().FULL_STATEMENT).set_response(statement_data)

            # get the standardized response
            response.update(accounts_resource.response())
            
            # if we are forwarding the recevied data
            if forward:

                # we are setting additional data that needs to be sent back to the callback url
                # they are optional data
                if saved_ipn.business_id is not None:
                    self.callback_payload = {
                        'business_organization_unit_id': str(saved_ipn.business_id)
                    }
                if saved_ipn.tenant_id is not None:
                    self.callback_headers = {
                        '__tenant': str(saved_ipn.tenant_id)
                    }
                callback_status=self._send_to_callback(
                    response, callback_url=saved_ipn.statement_url, callback_headers=self.callback_headers, callback_payload=self.callback_payload, sleep=False)           
                if isinstance(callback_status,dict):
                    # Here we indicate that the data was forwarded successfully

                    # The endpoint being forwarded the data can return a JSON response with a 'message' variable in it OR
                    # If the endpoint returns NO DATA a JSON response body is created with a 'code' variable in it, which holds the response code returned
                    # This is done in the 'api_request' method in the 'API' class, which is called/inherited by the '_send_to_callback' method in the 'Resource' class that is inherited in this class
                    response['callback_status_code']=callback_status.get("code", callback_status.get("message", -1))
            # if we are not forwading the received data 
            else:
                # indicate that the data was 'forwarded' successfully
                response['callback_status_code']=status.HTTP_200_OK
        except ObjectDoesNotExist:
            print("The IPN doesn't exist.")

        return response

    # This is a 'global' function
    # Used to get banks supported by Nash
    def bank_types_by_id(self, bank_id=None):
        return self.exec_global_function(operation=super().BANKS_BY_ID, bank_id=bank_id)

    # This is a 'global' function
    # Used to get banks supported by Nash
    def bank_types_by_code(self, bank_code=None):
        return self.exec_global_function(operation=super().BANKS_BY_CODE, bank_id=bank_code)

    def bank_payment_modes(self):
        return super().get_bank_payment_modes()

    # This is a 'global' function
    # Used to get sample_payloads for a resource's end point
    def sample_payload(self, bank_id=None, payload=None):
        return self.exec_global_function(operation=super().SAMPLE_DATA, bank_id=bank_id, payload=payload)

    # This is a 'global' function
    # Used to get sample_payloads for a resource's end point
    def countries(self, payload=None):
        return self.exec_global_function(operation=super().COUNTRIES, payload=payload)

    # This method is responsible for returning the bank id that's to execute the 'global' functions
    def exec_global_function(self, operation=0, bank_id=None, payload=None):
        data = {}
        # Set the operation to be performed
        super().set_operation(operation)

        # If a bank id is supplied
        if bank_id is not None:
            # If a user did not set a bank id
            if super().get_bank_id() < 1:
                # If a user did not set a bank id, set the bank_id to the Global Biller ID 0
                super().set_bank_id(super().GLOBAL)
                # Executing the method below after setting the Global Biller ID will ensure
                # that we are calling/get access to the SAMPLE_DATA operation found
                # linked to the Global ID. Pass the bank id whose sample data the user wants
                data = super().read(payload, params=f'bank_id={bank_id}')

            # If a user set a bank id
            elif super().get_bank_id() > 0:
                # Since operations are linked to a bank id, we want to get access to the Global Biller ID,
                # so as to get access to the SAMPLE_DATA operation, execute the call, then set bank id to
                # the user's bank ID

                # Get the user's bank id and save it temporarily (temp)
                temp = super().get_bank_id()
                # Set the bank id to the Global Biller ID
                super().set_bank_id(super().GLOBAL)

                # Execite the SAMPLE_DATA operation
                # Pass the bank id whose sample data the user wants
                data = super().read(payload, params=f'bank_id={bank_id}')

                # reset the bank_id to the bank id set by the user before (temp)
                super().set_bank_id(temp)

        # If a bank id is not supplied
        else:
            # If a user did not set a bank id
            if super().get_bank_id() < 1:
                # If a user did not set a bank id, set the bank_id to the Global Biller ID 0
                super().set_bank_id(super().GLOBAL)
                # Executing the method below after setting the Global Biller ID will ensure
                # that we are calling/get access to the SAMPLE_DATA operation found
                # linked to the Global ID. Pass the bank id whose sample data the user wants
                data = super().read(payload, params=f'bank_id={bank_id}')

            # If a user did set a bank id
            elif super().get_bank_id() > 0:
                # Since operations are linked to a bank id, we want to get access to the Global Biller ID,
                # so as to get access to the SAMPLE_DATA operation, execute the call, then set bank id to
                # the user's bank ID

                # Get the user's bank id and save it temporarily (temp)
                temp = super().get_bank_id()
                # Set the bank id to the Global Biller ID
                super().set_bank_id(super().GLOBAL)

                # Execite the SAMPLE_DATA operation
                # Pass the bank id whose sample data the user wants
                data = super().read(payload, params=f'bank_id={bank_id}')
                # Set bank id to back the user's orginal bank id
                super().set_bank_id(temp)

        # The 'if else' complexities above are done to ensure that the users can call this method
        # anywhere in their code, if they wish to get a sample data

        return data
