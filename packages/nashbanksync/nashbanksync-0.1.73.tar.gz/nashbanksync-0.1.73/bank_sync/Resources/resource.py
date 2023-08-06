from django.utils import timezone
from bank_sync.Resources.operations import Operations
from bank_sync.APIs.api_format import API
import json
from bank_sync.APIs.utils.generate_code import get_code
import hmac
import hashlib
import base64
import time
import threading
from django.core.exceptions import ObjectDoesNotExist
from bank_sync.Resources.helpers import IsDjangoAppClass
from datetime import datetime, date

_is_django_app = False
try:
    from bank_sync.models import Callbacks
    from bank_sync.models import IPNData
    from bank_sync.models import IPN
    _is_django_app = True
except Exception as e:
    _is_django_app = False

# This class will be inherited by sub entities e.g. Accounts Class and Payments Class
# It has common methods that these entities will override and implement
# As wll as methods that can be used by any of the Entities


class Resource(API, Operations):

    _bank_id = 0

    _operation = 0

    _user_id = None

    _response = {}

    # The standardized request
    _request = {}

    _callback_data = None

    _read_url = ""

    _api = None

    _resource_id = -1

    _action = 'read'

    _ipn_object = None

    # use this to add additonal payload to be sent to a callback
    callback_payload = {}
    # use this to add additonal headers to be sent to a callback
    callback_headers = {}

    @property
    def READ(self):
        return 0

    def set_action(self, action):
        self._action = action
        return self

    def set_operation(self, operation):
        self._operation = operation
        return self

    def set_bank_id(self, bank_id):
        self._bank_id = bank_id
        return self

    def set_user_id(self, user_id):
        self._user_id = user_id
        return self

    def set_urls(self, urls):
        self.set_read_url(urls.get("read", ""))
        return self

    def payload(self):
        return {}

    def serialize(self):
        return self

    def response(self):
        return self._response

    def request(self):
        return self._request

    def set_response(self, response={}):
        self._response = response
        return self

    def set_error(self, error):
        self._response = {"error": error}
        return self

    def set_request(self, request={}):
        self._request = request
        return self

    def set_read_url(self, read_url):
        self._read_url = read_url
        return self

    def get_read_url(self):
        return self._read_url

    def get_bank_id(self):
        return self._bank_id

    def get_user_id(self):
        return self._user_id

    def generate_code(self, length=6):
        return get_code(length)

    def get_operation(self):
        return self._operation

    def get_action(self):
        return self._action

    def get_bank_payment_modes(self):
        # use the Operation's super class to set the response that will be returned when this method is called
        self._response = super().BANK_PAYMENT_MODES
        return self

    # This is the data that can be sent back to a callback, it can be overriden
    # Each resource has the ability to decide what data can be sent back to a callback
    # This is the default standard of a sync callback data

    # You can use this method to simutalte a sync callback for endpoints that return data synchronously
    def sync_callback(self, response={}):
        # TODO implement a default method for sending async data
        pass

    def get_callback_data(self):
        return self._callback_data

    # The method used to execute the API calls to the Bank Integrations APIs
    # It uses methods/variables from the Operations Class to combine and create the appropriate API URL endpoint and method to be executed based on the banking operation to be perfomed
    def read(self, payload=None, params=''):
        # Check if the bank exists
        if self.get_bank_id() in self.BANKS_CONF.keys() or self.get_bank_id() in self.THIRD_PARTY_BANKING.keys():
            # set BANKS to be the default operation when no operation is passed
            # get a banks' API details
            if self.get_bank_id() in self.BANKS_CONF.keys():
                bank = self.BANKS_CONF.get(self.get_bank_id(), self.BANKS)
            elif self.get_bank_id() in self.THIRD_PARTY_BANKING.keys():
                bank = self.THIRD_PARTY_BANKING.get(
                    self.get_bank_id(), self.BANKS)

            endpoint = bank.get(self.get_action(), {}).get('endpoint', '')

            operation, method = bank.get(self.get_action(), {}).get(
                'operations', {}).get(self.get_operation(), (-1, -1))

            if operation == -1 and method == -1:
                self._response = {
                    'error': f'Bank ID {self.get_bank_id()} Does not have Operation {self.get_operation()} in {self.get_action()} Entity'}
            else:
                # Check if any query params where passed, while creating the end point
                if bool(params):
                    endpoint = f'{endpoint}/{operation}?{params}'
                else:
                    endpoint = f'{endpoint}/{operation}'

                super().set_full_url(
                    full_url=f"{bank.get('url','')}/{endpoint}")

                # Call the method exec to make the request to A.P.I. endpoint and return the data that will be returned in this method
                self._response = self._exec(payload, method)
                print(f'json.loads(self._response.text) 4: {self._response}')


        else:
            self._response = {'error': 'Bank ID Does not Exist'}
        return self

    # This is the method that will be called execute an A.P.I. request.
    # Since most of the A.P.I. calls methods are similar, they are to be placed inside this method to avoid code duplication.
    #
    # It will only accept parameters unique to each A.P.I. request.
    def _exec(self, payload=None, method='POST', files=None):

        # NCBA send data back to our callback as XML converted to bytes
        if isinstance(payload, bytes):
            payload = payload.decode("utf-8")

        if files is None:
            payload = json.dumps(payload)
        else:
            payload = payload

        # Call the A.P.I. url by passing the variables to the super class method responsible for making requests to A.P.I. endpoints
        # The super class method returns a response that is returned by this method
        return super().api_request(payload=payload, method=method, files=files)

    # Use this method to standardize the callbacks sent by the payments resource get the serialised/standardized response
    # and add aditional identifiable data to it
    # This method is used to simulate callbacks for banks or operations that return data synchronously
    # This method is also used by banks that do not return a transaction reference in the synchronous data, otherwise this
    # would have been handled by the core integrations
    @IsDjangoAppClass(_is_django_app)
    def simulate_callback(self, response={}):
        if self.get_bank_id() in [super().EQUITY]:
            if self.get_operation() not in [super().MOBILE_WALLET]:
                # get the standardized request
                request = self.request()
                response["bank_id"] = self.get_bank_id()
                response["type"] = self.get_operation()

                # Equity bank retunrs data synchronously, we will append to it unique identifiers that are not returned
                # e.g. our unique bank id and type of operation/transaction performed
                if self.get_bank_id() == super().EQUITY:
                    response["code"] = f'{int(response.get("code"))}'
                    response["completed"] = False
                    response["account_reference"] = request.get(
                        "transfer", {}).get("reference", "")
                    response["account_source"] = request.get(
                        "source", {}).get("account_number", "")
                    response["account_destination"] = request.get(
                        "destinations", [])[0].get("account_number", "")
                    response["amount"] = f'{request.get("destinations", [])[0].get("amount", -1)}'

                    if int(response.get("code")) == 0:
                        response["completed"] = True

                    callback_url = request.get(
                        "transfer", {}).get("callback_url", "")
                    print(f'__tenant: {request.get("__tenant", None)}')
                    # we are setting additional data that needs to be sent back to the callback url
                    # they are optional data
                    if request.get("business_organization_unit_id", None) is not None:
                        self.callback_payload['business_organization_unit_id']=request.get("business_organization_unit_id", None)
                    if request.get("counter_party_type", None) is not None:
                        self.callback_payload['counter_party_type']=request.get("counter_party_type", None)
                    if request.get("__tenant", None) is not None:
                        self.callback_headers = {
                            '__tenant': request.get("__tenant", None)
                        }
                    print(f'self.callback_headers: {self.callback_headers}')
                    # simultate a callback by sending data later via a thread
                    # this will only work if a callback was sent/placed in the standardized payload
                    threading.Thread(target=self._send_to_callback,
                                     args=[response, callback_url, self.callback_payload, self.callback_headers]).start()

    # This method is used to standardize callbacks received after they were registered by the register_callback method below
    @IsDjangoAppClass(_is_django_app)
    def standardize_callback(self, callback_data={}, forward=True):

        response = {
            "completed": False,
            "type": callback_data.get("type", -1),
            "bank_id": callback_data.get("bank_id", -1)
        }

        try:

            # Use the reference of the callback sent to get the callback data that was linked to the operation
            # This will returns a queryset, you will use .first() method or len() to manipultate it
            saved_callback = Callbacks.objects.get(
                reference=callback_data.get("reference", ""))

            self.save_callback_data(saved_callback, callback_data)

            callback = None

            # The bank id and type sent here, will be used to know how to standardize the data received

            if callback_data.get("bank_id", -1) == super().COOP:

                callback = saved_callback

                if callback_data.get("type", -1) in [super().IFT, super().MOBILE_WALLET, super().PESALINK_TO_BANK, super().PESALINK_TO_MOBILE]:

                    response["code"] = f'{int(callback_data.get("MessageCode", callback_data.get("messageCode", -1)))}'
                    response["account_reference"] = callback_data.get(
                        "reference", "")
                    response["date"] = callback_data.get(
                        "MessageDateTime", callback_data.get("messageDateTime", ""))

                    if 'Source' in callback_data.keys():
                        response["account_source"] = callback_data.get(
                            "Source", {}).get("AccountNumber", "")
                    elif 'source' in callback_data.keys():
                        response["account_source"] = callback_data.get(
                            "source", {}).get("accountNumber", "")

                    if 'Source' in callback_data.keys():
                        response["message"] = callback_data.get(
                            "Source", {}).get("ResponseDescription", "")
                    elif 'source' in callback_data.keys():
                        response["message"] = callback_data.get(
                            "source", {}).get("responseDescription", "")

                    if 'Destinations' in callback_data.keys():
                        if isinstance(callback_data.get("Destinations", {}), dict):
                            response["account_destination"] = callback_data.get(
                                "Destinations", {}).get("AccountNumber", "")
                        if isinstance(callback_data.get("Destinations", []), list):
                            response["account_destination"] = callback_data.get(
                                "Destinations", [])[0].get("AccountNumber", "")

                            if callback.type_code == super().MOBILE_WALLET:
                                response["account_destination"] = callback_data.get(
                                    "Destinations", [])[0].get("MobileNumber", "")
                            elif callback.type_code == super().PESALINK_TO_MOBILE:
                                response["account_destination"] = callback_data.get(
                                    "Destinations", [])[0].get("PhoneNumber", "")

                    elif 'destination' in callback_data.keys():
                        response["account_destination"] = callback_data.get(
                            "destination", {}).get("accountNumber", "")

                    if 'Destinations' in callback_data.keys():
                        if isinstance(callback_data.get("Destinations", {}), dict):
                            response["transaction_id"] = callback_data.get(
                                "Destinations", {}).get("TransactionID", "")
                        if isinstance(callback_data.get("Destinations", []), list):
                            response["transaction_id"] = callback_data.get(
                                "Destinations", [])[0].get("TransactionID", "")
                    elif 'destination' in callback_data.keys():
                        response["transaction_id"] = callback_data.get(
                            "destination", {}).get("transactionID", "")

                    if 'Destinations' in callback_data.keys():
                        if isinstance(callback_data.get("Destinations", {}), dict):
                            response["amount"] = f'{callback_data.get("Destinations", {}).get("Amount", "")}'
                        if isinstance(callback_data.get("Destinations", []), list):
                            response["amount"] = f'{callback_data.get("Destinations", [])[0].get("Amount", "")}'
                    elif 'destination' in callback_data.keys():
                        response["amount"] = f'{callback_data.get("destination", {}).get("amount", "")}'

                    if int(response.get("code")) == 0:
                        response["completed"] = True

            elif callback_data.get("bank_id", -1) == super().EQUITY:

                callback = saved_callback

                if callback_data.get("type", -1) == super().MOBILE_WALLET:

                    # if len(saved_callback):
                    #     callback = saved_callback.first()
                    # callback = saved_callback
                    response.update({
                        "message": f'{callback_data.get("message", "")}: {callback_data.get("data", {}).get("ResponseDescription","")}',
                        "code": f'{round(float(callback_data.get("code", -1)), 2)}',
                        "transaction_id": callback_data.get("data", {}).get("ThirdPartyTranID", ""),
                        "date": callback.request.get("transfer", {}).get('date', ""),
                        "account_reference": callback_data.get("transactionReference", ""),
                        "account_source": f"{callback.request.get('source',{}).get('account_number','')} {callback.request.get('source',{}).get('name','')}",
                        "account_destination": callback_data.get("data", {}).get("ReceiverMsisdn", ""),
                        "amount": f"{round(float(callback.request.get('source', {}).get('amount', -1)), 2)}"
                    })

                    if int(float(response.get("code"))) == 0:
                        response["completed"] = True

                elif callback_data.get("type", -1) == super().PDF_TO_JSON:
                    # if len(saved_callback):
                    #     callback = saved_callback.first()
                    # callback = saved_callback
                    response = self.standardize_pdf_to_json(
                        response_data=callback_data)

            # This is a variable used to forward the standardized callback data to another callback url
            # If it was supplied ans saved, else return the standardized response back to the
            if forward:
                if callback is not None:

                    # we are setting additional data that needs to be sent back to the callback url
                    # they are optional data
                    if callback.business_id is not None:                        
                        self.callback_payload['business_organization_unit_id']=str(callback.business_id)
                    if callback.counter_party_type is not None:
                        self.callback_payload['counter_party_type']=str(callback.counter_party_type)
                    if callback.tenant_id is not None:
                        self.callback_headers = {
                            '__tenant': str(callback.tenant_id)
                        }
                    
                    self._send_to_callback(
                        response, callback_url=callback.callback, callback_headers=self.callback_headers, callback_payload=self.callback_payload, sleep=False)

        except ObjectDoesNotExist:
            print("The callback doesn't exist.")

        return response

    # This method is used to standardize IPN responses received
    @IsDjangoAppClass(_is_django_app)
    def standardize_ipn(self, ipn_data={}, forward=True):

        ipn = None

        response = {
            "completed": False,
            "type": ipn_data.get("type", -1),
            "bank_id": ipn_data.get("bank_id", -1),
        }

        try:

            # Use the reference of the callback sent to get the callback data that was linked to the operation
            # This will returns a queryset, you will use .first() method or len() to manipultate it
            saved_ipn = IPN.objects.get(
                client_id=ipn_data.get("client_id", ""), bank_id=ipn_data.get("bank_id", ""), account_number=ipn_data.get("account_number"))

            # if len(saved_ipn):
            #     # get the IPN
            #     ipn = saved_ipn.first()
            ipn = saved_ipn

            # save the response sent back to the ipn
            self.save_ipn_data(saved_ipn, ipn_data)

            if ipn_data.get("bank_id", -1) == super().EQUITY:

                if ipn_data.get("type", -1) in [super().OMN,super().POLARIS_CHANNEL,super().MISYS]:

                    response.update({
                        "message": f'{ipn_data.get("transaction", {}).get("status","")} {ipn_data.get("transaction", {}).get("remarks", "")}',
                        "code": f'{ipn_data.get("code", "-1")}',
                        "transaction_id": ipn_data.get("bank", {}).get("reference", "").strip(),
                        "date": ipn_data.get("transaction", {}).get('date', ""),
                        "account_reference": f'{ipn_data.get("customer", {}).get("reference", "").strip()}',
                        "account_source": f"{ipn_data.get('bank',{}).get('account','')}",
                        "account_destination": ipn_data.get("transaction", {}).get("remarks", ""),
                        "amount": f"{ipn_data.get('transaction', {}).get('amount', -1)}",
                        "transaction_type": ipn_data.get('bank', {}).get('transactionType', '').lower(),
                    })

                    if ipn_data.get('bank', {}).get("transactionType", '').lower() == 'credit':
                        response["account_source"] = ipn_data.get(
                            "transaction", {}).get("remarks", "")
                        response["account_destination"] = f"{ipn_data.get('bank',{}).get('account','')}"

                    if int(response.get("code")) == 0:
                        response["completed"] = True

                    if ipn_data.get("type", -1) == super().MISYS:
                        response["account_reference"] = f'{ipn_data.get("transaction", {}).get("reference", "").strip()}'

            elif ipn_data.get("bank_id", -1) == super().COOP:

                response.update({
                    "message": f'{ipn_data.get("Narration", "")}',
                    "code": f'{ipn_data.get("code", "-1")}',
                    "transaction_id": ipn_data.get("TransactionId", "").strip(),
                    "date": datetime.strptime(ipn_data.get("TransactionDate", ""), '%Y-%m-%dT%H:%M:%S.%f%z').strftime("%Y:%m:%d %H:%M:%S"),
                    "account_reference": f'{ipn_data.get("MessageReference", "").strip()}',
                    "account_source": f"{ipn_data.get('AccountNumber','')}",
                    "account_destination": f'{ipn_data.get("CustMemo", {}).get("CustMemoLine3", "")} {ipn_data.get("CustMemo", {}).get("CustMemoLine2", "")}',
                    "amount": f'{ipn_data.get("Amount", "-1")}',
                    "transaction_type": ipn_data.get('EventType', '').lower(),
                })

                if ipn_data.get("EventType", '').lower() == 'credit':
                    response["account_source"] = f'{ipn_data.get("CustMemo", {}).get("CustMemoLine3", "")} {ipn_data.get("CustMemo", {}).get("CustMemoLine2", "")}'
                    response["account_destination"] = f"{ipn_data.get('AccountNumber','')}"

                if int(response.get("code")) == 0:
                    response["completed"] = True

            elif ipn_data.get("bank_id", -1) == super().NCBA:
                response.update({
                    "message": f'{ipn_data.get("phone_nr", "")} {ipn_data.get("narrative", "")}',
                    "transaction_id": ipn_data.get("trans_id", "").strip(),
                    # TODO IPN NCBA Date dev
                    "date": ipn_data.get("date", date.today().strftime('%Y:%m:%d %H:%M:%S')),
                    "account_reference": f'{ipn_data.get("reference", "").strip()}',
                    "account_source": f"{ipn_data.get('account_nr','')}",
                    "account_destination": f'{ipn_data.get("customer_name", "")}',
                    "amount": f'{ipn_data.get("trans_ammount", "-1")}',
                    "transaction_type": ipn_data.get('type', '').lower(),
                })

                if ipn_data.get("type", '').lower() == 'credit':
                    response["account_source"] = f'{ipn_data.get("customer_name", "")}'
                    response["account_destination"] = f"{ipn_data.get('account_nr','')}"

                if ipn_data.get("status", "") == "SUCCESS":
                    response["completed"] = True
                    response["code"] = 0

            # This is a variable used to forward the standardized ipn data to another callback url
            # If it was supplied and saved, else return the standardized response back to the
            if forward:
                if ipn is not None:
                    # we are setting additional data that needs to be sent back to the callback url
                    # they are optional data
                    if ipn.business_id is not None:
                        self.callback_payload['business_organization_unit_id']=str(ipn.business_id)
                    if ipn.tenant_id is not None:
                        self.callback_headers = {
                            '__tenant': str(ipn.tenant_id)
                        }
                    self._send_to_callback(
                        response, callback_url=ipn.url, callback_headers=self.callback_headers, callback_payload=self.callback_payload, sleep=False)

        except ObjectDoesNotExist:
            print("The IPN doesn't exist.")

        return response

    # This method is used to standardize pdf_to_json responses
    def standardize_pdf_to_json(self, response_data):
        std_data_list = []
        std_data = {}

        if self.get_bank_id() == super().SAFCOM:
            if isinstance(response_data, dict):
                statement_type = response_data.get("statement_type", None)
                data = response_data.get("data", [])
                if statement_type == 'personal':
                    for i in range(len(data)):
                        std_data = {
                            "date": data[i].get("completion_time", ""),


                            "description": data[i].get("details", ""),
                            "reference": data[i].get("receipt_no", ""),
                            "running_balance": data[i].get("balance", ""),
                        }

                        if data[i].get("details") is None:
                            std_data['description'] = data[i].get(
                                "transaction", "")

                        if data[i].get("paid_in") is not None:
                            if float(str(data[i].get("paid_in", "-1")).replace(',', '')) > 0:
                                std_data['type'] = 'credit'
                                std_data['amount'] = str(
                                    float(str(data[i].get("paid_in", "-1")).replace(',', '')))

                        if data[i].get("withdraw") is not None:
                            if float(str(data[i].get("withdraw", "-1")).replace(',', '')) > 0:
                                std_data['type'] = 'debit'
                                std_data['amount'] = str(
                                    float(str(data[i].get("withdraw", "-1")).replace(',', '')))
                            elif float(str(data[i].get("withdraw", "-1")).replace(',', '')) < 0:
                                std_data['type'] = 'debit'
                                std_data['amount'] = str(
                                    float(str(data[i].get("withdraw", "-1")).replace(',', ''))*-1)

                        std_data['running_balance'] = str(
                            std_data['running_balance'])

                        std_data_list.append(std_data)

        elif self.get_bank_id() == super().DTB:
            if isinstance(response_data, dict):
                statement_type = response_data.get("statement_type", None)
                data = response_data.get("data", [])
                if statement_type == 'personal':
                    for i in range(len(data)):
                        std_data = {
                            "date": data[i].get("transaction", ""),
                            "currency_code": data[i].get("currency", ""),


                            "description": f'{data[i].get("transaction_type", "")} {data[i].get("transaction_details", "")}',
                            "reference": data[i].get("reference", ""),
                            "running_balance": data[i].get("balance", "")
                        }

                        if data[i].get("credits", -1) > 0 or data[i].get("debits", -1) < 0:
                            std_data['type'] = 'credit'
                            if data[i].get("credits", -1) > 0:
                                std_data['amount'] = f'{data[i].get("credits", -1)}'
                            elif data[i].get("debits", -1) < 0:
                                std_data['amount'] = f'{data[i].get("debits", -1)*-1}'

                        if data[i].get("debits", -1) > 0:
                            std_data['type'] = 'debit'
                            std_data['amount'] = f'{data[i].get("debits", -1)}'

                        std_data['running_balance'] = str(
                            std_data['running_balance'])
                        std_data_list.append(std_data)

        elif self.get_bank_id() == super().EQUITY:
            if isinstance(response_data, dict):
                statement_type = response_data.get("statement_type", None)
                data = response_data.get("data", [])
                if statement_type == 'personal':
                    for i in range(len(data)):
                        std_data = {
                            "date": data[i].get("date", ""),
                            "currency_code": data[i].get("currency", ""),


                            "description": f'{data[i].get("transaction_details", "")}',
                            "reference": "",
                            "running_balance": data[i].get("balance", ""),
                            "type": data[i].get("type", ""),
                            "amount": data[i].get("amount", ""),
                        }

                        std_data['running_balance'] = str(
                            std_data['running_balance'])
                        std_data['amount'] = str(std_data['amount'])

                        std_data_list.append(std_data)
                elif statement_type == 'business':
                    for i in range(len(data)):
                        std_data = {
                            "date": data[i].get("date", ""),
                            "currency_code": data[i].get("currency", ""),


                            "description": f'{data[i].get("transaction_details", "")}',
                            "reference": "",
                            "running_balance": data[i].get("balance", ""),
                            "type": data[i].get("type", ""),
                            "amount": data[i].get("amount", ""),
                        }

                        std_data['running_balance'] = str(
                            std_data['running_balance'])
                        std_data['amount'] = str(std_data['amount'])

                        std_data_list.append(std_data)

        elif self.get_bank_id() == super().COOP:
            if isinstance(response_data, dict):
                statement_type = response_data.get("statement_type", None)
                data = response_data.get("data", [])
                if statement_type == 'personal':
                    for i in range(len(data)):
                        std_data = {
                            "date": data[i].get("transaction_date", ""),
                            "currency_code": data[i].get("currency", ""),


                            "description": f'{data[i].get("transaction_details", "")}',
                            "reference": data[i].get("reference_number", ""),
                            "running_balance": data[i].get("balance", ""),
                            "type": data[i].get("type", ""),
                            "amount": data[i].get("amount", ""),
                        }

                        std_data['running_balance'] = str(
                            std_data['running_balance'])
                        std_data['amount'] = str(std_data['amount'])

                        std_data_list.append(std_data)
                elif statement_type == 'business':
                    pass

        elif self.get_bank_id() == super().NCBA:
            if isinstance(response_data, dict):
                statement_type = response_data.get("statement_type", None)
                data = response_data.get("data", [])
                if statement_type == 'personal':
                    for i in range(len(data)):
                        std_data = {
                            "date": data[i].get("date", ""),
                            "currency_code": data[i].get("currency", ""),


                            "description": f'{data[i].get("transaction_type", "")} {data[i].get("transaction_details", "")}',
                            "reference": data[i].get("reference", ""),
                            "running_balance": data[i].get("balance", ""),
                            "type": data[i].get("type", ""),
                            "amount": data[i].get("amount", ""),
                        }

                        std_data['running_balance'] = str(
                            std_data['running_balance'])
                        std_data['amount'] = str(std_data['amount'])

                        std_data_list.append(std_data)

        elif self.get_bank_id() == super().SCB:
            if isinstance(response_data, dict):
                statement_type = response_data.get("statement_type", None)
                data = response_data.get("data", [])
                if statement_type == 'personal':
                    for i in range(len(data)):
                        std_data = {
                            "date": data[i].get("entry_date", ""),
                            "currency_code": data[i].get("currency", ""),


                            "description": f'{data[i].get("description", "")}',
                            "reference": data[i].get("reference", ""),
                            "running_balance": data[i].get("balance", ""),

                            "type": data[i].get("type", ""),
                            "amount": data[i].get("amount", ""),
                        }

                        if data[i].get("deposit", -1) > 0:
                            std_data['type'] = 'credit'
                            std_data['amount'] = f'{data[i].get("deposit", -1)}'
                        if data[i].get("withdrawal", -1) > 0:
                            std_data['type'] = 'debit'
                            std_data['amount'] = f'{data[i].get("withdrawal", -1)}'

                        std_data['running_balance'] = str(
                            std_data['running_balance'])

                        std_data_list.append(std_data)

        elif self.get_bank_id() == super().KCB:
            if isinstance(response_data, dict):
                statement_type = response_data.get("statement_type", None)
                data = response_data.get("data", [])
                if statement_type == 'business':
                    data = response_data.get("data", [])
                    for i in range(len(data)):
                        std_data = {
                            "date": data[i].get("transaction_date", ""),
                            "currency_code": data[i].get("currency", ""),


                            "description": f'{data[i].get("transaction_details", "")}',
                            "reference": data[i].get("bank_reference_number", ""),
                            "running_balance": data[i].get("balance", ""),
                        }

                        if data[i].get("money_in", -1) > 0:
                            std_data['type'] = 'credit'
                            std_data['amount'] = f'{data[i].get("money_in", -1)}'
                        if data[i].get("money_out", -1) > 0:
                            std_data['type'] = 'debit'
                            std_data['amount'] = f'{data[i].get("money_out", -1)}'

                        std_data['running_balance'] = str(
                            std_data['running_balance'])

                        std_data_list.append(std_data)

        elif self.get_bank_id() == super().FAULU:
            if isinstance(response_data, dict):
                statement_type = response_data.get("statement_type", None)
                data = response_data.get("data", [])
                if statement_type == 'personal':
                    for i in range(len(data)):
                        std_data = {
                            "date": data[i].get("book_date", ""),
                            "currency_code": data[i].get("currency", ""),


                            "description": f'{data[i].get("description", "")}',
                            "reference": data[i].get("reference", ""),
                            "running_balance": data[i].get("balance", ""),
                            "amount": data[i].get("amount", ""),
                            "type": data[i].get("type", ""),
                        }

                        std_data['running_balance'] = str(
                            std_data['running_balance'])
                        std_data['amount'] = str(std_data['amount'])

                        std_data_list.append(std_data)

        elif self.get_bank_id() == super().CONSOLIDATED:
            if isinstance(response_data, dict):
                statement_type = response_data.get("statement_type", None)
                data = response_data.get("data", [])
                if statement_type == 'personal':
                    for i in range(len(data)):
                        std_data = {
                            "date": data[i].get("transaction_date", ""),
                            "currency_code": data[i].get("currency", ""),


                            "description": f'{data[i].get("description", "")}',
                            "reference": data[i].get("reference", ""),
                            "running_balance": data[i].get("balance", ""),
                            "amount": data[i].get("amount", ""),
                            "type": data[i].get("type", ""),
                        }

                        std_data['running_balance'] = str(
                            std_data['running_balance'])
                        std_data['amount'] = str(std_data['amount'])

                        std_data_list.append(std_data)

        elif self.get_bank_id() == super().STANBIC:
            if isinstance(response_data, dict):
                statement_type = response_data.get("statement_type", None)
                data = response_data.get("data", [])
                if statement_type == 'personal':
                    for i in range(len(data)):
                        std_data = {
                            "date": data[i].get("date", ""),
                            "currency_code": data[i].get("currency", ""),


                            "description": f'{data[i].get("transaction", "")}',
                            "reference": data[i].get("reference", ""),
                            "running_balance": data[i].get("available_balance", ""),
                            "amount": data[i].get("amount", ""),
                            "type": data[i].get("type", ""),
                        }

                        std_data['running_balance'] = str(
                            std_data['running_balance'])
                        std_data['amount'] = str(std_data['amount'])

                        std_data_list.append(std_data)

        elif self.get_bank_id() == super().FAMILY:
            if isinstance(response_data, dict):
                statement_type = response_data.get("statement_type", None)
                data = response_data.get("data", [])
                if statement_type == 'personal':
                    for i in range(len(data)):
                        std_data = {
                            "date": data[i].get("value_date", ""),
                            "currency_code": data[i].get("currency", ""),


                            "description": f'{data[i].get("description", "")}',
                            "reference": data[i].get("reference", ""),
                            "running_balance": data[i].get("running_balance", ""),
                            "amount": data[i].get("amount", ""),
                            "type": data[i].get("transaction_type", ""),
                        }

                        std_data['running_balance'] = str(
                            std_data['running_balance'])
                        std_data['amount'] = str(std_data['amount'])

                        std_data_list.append(std_data)

        elif self.get_bank_id() == super().NCBA_LOOP:
            if isinstance(response_data, dict):
                statement_type = response_data.get("statement_type", None)
                data = response_data.get("data", [])
                if statement_type == 'personal':
                    for i in range(len(data)):
                        std_data = {
                            "date": data[i].get("value_date", ""),
                            "currency_code": data[i].get("currency", ""),


                            "description": f'{data[i].get("transaction_details", "")}',
                            "reference": data[i].get("reference_number", ""),
                            "running_balance": data[i].get("balance", ""),
                            "amount": data[i].get("amount", ""),
                            "type": data[i].get("type", ""),
                        }

                        std_data['running_balance'] = str(
                            std_data['running_balance'])
                        std_data['amount'] = str(std_data['amount'])

                        std_data_list.append(std_data)

        data = {"data": std_data_list}
        if isinstance(response_data, dict):
            data['doc_code'] = response_data.get("doc_code", None)
            if 'error' in response_data.keys():
                data['error'] = response_data.get("error", None)
            if 'message' in response_data.keys():
                data['message'] = response_data.get("message", None)

            if len(response_data.get("data", [])):
                data['account_number'] = response_data.get(
                    "data", [])[0].get("account_number", "")
                data['account_name'] = response_data.get(
                    "data", [])[0].get("account_name", "")

        return data

    # Use this method to set an operation/transaction to save/register callbacks business_id
    # When an operation is called with this method, it saves the callback url sent and the reference
    # This method regesiters callbacks for banks that return data as a callback with the reference sent
    @IsDjangoAppClass(_is_django_app)
    def register_callback(self):
        save_callback = True
        reference = None
        callback = None

        # check if the bank id is of COOP or EQUITY
        # if self.get_bank_id() in [super().COOP, super().EQUITY]:
        #     # If it is Equity confirm that the payment operation to be done is not a Bank to Mpesa or PDF to JSON
        #     if super().EQUITY == self.get_bank_id() and self.get_operation() not in [super().MOBILE_WALLET, super().PDF_TO_JSON]:
        #         # if so set the save_callback to False, stating that we do not want to store its data in the callback table
        #         save_callback = False

        if save_callback:
            # Get the request that was sent
            request = self.request()

            # save the reference, callback, bank id and operation
            if super().EQUITY == self.get_bank_id() and self.get_operation() == super().PDF_TO_JSON:
                reference = request.get("reference", "")
                callback = request.get("callback_url", "")
            else:
                reference = request.get("transfer", {}).get("reference", "")
                callback = request.get("transfer", {}).get("callback_url", "")

            if reference != '' and callback != '':
                Callbacks.objects.create(reference=reference, tenant_id=request.get("__tenant", None), business_id=request.get("business_organization_unit_id", None),
                                         counter_party_type=request.get("counter_party_type", None), callback=callback,
                                         request=request, bank_id=self.get_bank_id(), type_code=self.get_operation())

    # This method is used to save callback responses received
    @IsDjangoAppClass(_is_django_app)
    def save_callback_data(self, saved_callback, callback_data):
        callback = saved_callback
        callback.response = callback_data
        callback.response_time = timezone.now()
        callback.save()

    # This method is used to save IPN responses received
    @IsDjangoAppClass(_is_django_app)
    def save_ipn_data(self, saved_ipn, ipn_data):
        saved_ipn = saved_ipn
        IPNData.objects.create(ipn=saved_ipn, response=ipn_data)

    # This method is used to generate a signature
    def generate_signature(self, secret, message):
        digest = hmac.new(secret.encode(), msg=message.encode(
        ), digestmod=hashlib.sha256).digest()
        return base64.b64encode(digest).decode()

    # Use this method to send data to a saved callback URL
    def _send_to_callback(self, response, callback_url='', callback_payload={}, callback_headers={}, sleep=True, sleep_time=1):
        # if sleep has been set to true, sleep for the specified sleep time
        if sleep:
            time.sleep(1*sleep_time)
        # check if there is a callback url
        if callback_url != '':
            # check if there is additional data that you want to append to the response to be sent
            if bool(callback_payload):
                response.update(callback_payload)

            # set the response you want to be sent
            payload = json.dumps(response)

            # set the headers you want to be sent
            headers = {'Content-Type': 'application/json'}
            # check if there is additional headers that you want to append to the headers to be sent
            if bool(callback_headers):
                headers.update(callback_headers)

            self.set_headers(headers=headers)
            self.set_full_url(callback_url)
            response=self.api_request(payload=payload,
                             method='POST', verify=True)
        return response
