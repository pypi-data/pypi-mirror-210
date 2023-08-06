from bank_sync.Resources.resource import Resource
from bank_sync.APIs.utils.generate_code import get_code
from datetime import datetime, date
import json
try:
    from django.conf import settings
except Exception as e:
    pass

import logging
logger = logging.getLogger(__name__)


class Accounts(Resource):

    urls = {}
    bank_sync_call_back = {}

    full_statement_transaction_dict = {
        "currency_code": "",
        "date": "",
        "description": "",
        "transaction_id": "",
        "reference": "",
        "value_date": "",
        "posted_date": "",
        "service_point": "",
        "running_cleared_balance": "0",
        "debit_limit": "0",
        "limit_expiry_date": "",
        "serial": "",
        "amount": "0",
        "type": "",
        "transactions_count": "0"
    }

    try:
        bank_sync_call_back = getattr(
            settings, 'BANK_SYNC_CALL_BACK_URLS', bank_sync_call_back)
    except Exception as e:
        pass

    def set_bank_id(self, bank_id):
        # This is done to help with URL standardization in the operations and resource classes
        super().set_action(action='accounts')
        return super().set_bank_id(bank_id)

    def forex_rate(self, payload=None):

        return super().read(payload=payload)

    def balance(self, payload=None):

        return super().read(payload=payload)

    def mini_statement(self, payload=None):

        return super().read(payload=payload)

    def full_statement(self, payload=None):

        return super().read(payload=payload)

    def account_validation(self, payload=None):

        return super().read(payload=payload)

    def account_transactions(self, payload=None):

        return super().read(payload=payload)

    def pdf_to_json(self, payload=None):
        self.register_callback()
        return super().read(payload=payload)

    def get_pdf_json(self, payload=None):

        return super().read(payload=payload)

    def serialize(self, payload=None, operation=None):
        # Set the Operation being executed
        # Set the Original request sent before serialization
        super().set_operation(operation).set_request(payload)
        data = {}

        if operation in [super().PDF_TO_JSON]:
            data.update({
                "bank_id": super().get_bank_id(),
                "type": super().get_operation(),
                "bank_sync_call_back": self.bank_sync_call_back.get("payments", ""),
            })

        if operation is None:
            return "Specify the operation: Resource.BALANCE, Resource.MINI_STATEMENT, Resource.FULL_STATEMENT, Resource.ACCOUNT_VALIDATION or Resource.ACCOUNT_TRANSACTIONS"

        if operation == super().BALANCE or operation == super().MINI_STATEMENT or operation == super().ACCOUNT_VALIDATION:

            # If bank_id is COOP
            if super().get_bank_id() == super().COOP:
                data.update({
                    "MessageReference": f'{get_code(length=14)}',
                    "AccountNumber": f'{payload.get("account_number", "")}'
                })
            # If bank_id is EQUITY
            elif super().get_bank_id() == super().EQUITY:
                data.update({
                    "country_code": payload.get("country_code", ""),
                    "account_number": payload.get("account_number", "")
                })
            # If bank_id is NCBA
            elif super().get_bank_id() == super().NCBA:
                pass
            # If bank_id is UBA
            elif super().get_bank_id() == super().UBA:
                data.update({
                    "PROCESSING_CODE": 31,
                    "COUNTRY_CODE": payload.get("country_code", ""),
                    "DR_ACCT_NUM": payload.get("account_number", "")
                })
            # If bank_id is DTB
            elif super().get_bank_id() == super().DTB:
                if operation == super().ACCOUNT_VALIDATION:
                    data.update({
                        "account_number": payload.get("account_number", "")
                    })
            # If bank_id is THIRD_PARTY_BANKING
            elif super().get_bank_id() in super().THIRD_PARTY_BANKING.keys():
                data.update({
                    "businessCode": payload.get("business_code", ""),
                    "accountIds": [payload.get("account_number", "")]
                })

        elif operation == super().FULL_STATEMENT:
            # If bank_id is COOP
            if super().get_bank_id() == super().COOP:
                data.update({
                    "MessageReference": payload.get("reference", get_code(length=14)),
                    "AccountNumber": f'{payload.get("account_number", "")}',
                    "StartDate": payload.get("start_date", ""),
                    "EndDate": payload.get("end_date", "")
                })
            # If bank_id is EQUITY
            elif super().get_bank_id() == super().EQUITY:
                data.update({
                    "country_code": payload.get("country_code", ""),
                    "account_number": f'{payload.get("account_number", "")}',
                    "start_date": payload.get("start_date", ""),
                    "end_date": payload.get("end_date", ""),
                    "limit": payload.get("limit", 3),
                    "reference": payload.get("reference", get_code(length=14))
                })
            # If bank_id is NCBA
            elif super().get_bank_id() == super().NCBA:
                pass
            # If bank_id is UBA
            elif super().get_bank_id() == super().UBA:
                data.update({
                    "PROCESSING_CODE": 93,
                    "COUNTRY_CODE": payload.get("country_code", ""),
                    "DR_ACCT_NUM": payload.get("account_number", ""),
                    "TRAN_CRNCY_CODE": payload.get("currency_code", ""),
                    "STMT_QUERY_PARAMS": {
                        "START_DATE": payload.get("start_date", date.today().strftime('%Y%m%d')).replace("-", ""),
                        "END_DATE": payload.get("end_date", date.today().strftime('%Y%m%d')).replace("-", ""),
                        "NUM_TRANS": payload.get("limit", 5)
                    }
                })

        elif operation == super().ACCOUNT_TRANSACTIONS:
            # If bank_id is COOP
            if super().get_bank_id() == super().COOP:
                data.update({
                    "MessageReference": f'{get_code(length=14)}',
                    "AccountNumber": f'{payload.get("account_number", "")}',
                    "NoOfTransactions": f'{payload.get("limit", 1)}'
                })
            # If bank_id is EQUITY
            elif super().get_bank_id() == super().EQUITY:
                pass

            # If bank_id is NCBA
            elif super().get_bank_id() == super().NCBA:
                pass
            # If bank_id is THIRD_PARTY_BANKING
            elif super().get_bank_id() in super().THIRD_PARTY_BANKING.keys():
                data.update({
                    "businessCode": payload.get("business_code", ""),
                    "narration": payload.get("narration", ""),
                    "type": payload.get("type", ""),
                    "paginate": payload.get("paginate", True),
                    "startDate": payload.get("start_date", ""),
                    "endDate": payload.get("end_date", ""),
                    "limit": payload.get("limit", 1),
                    "total": payload.get("total", 0),
                    "offset": payload.get("offset", 0),
                    "accountIds": [payload.get("account_number", "")],

                })

        elif operation == super().PDF_TO_JSON or operation == super().GET_JSON_PDF:
            # data = payload
            data.update(payload)
            if payload.get("callback_url", None) is None or payload.get("callback_url", '') == '':
                data['bank_sync_call_back'] = payload.get("callback_url", None)

        elif operation == super().FOREX_RATE:
            if super().get_bank_id() == super().EQUITY:
                data.update({
                    "accountNumber": payload.get("account_number", ""),
                    "countryCode": payload.get("country_code", ""),
                    "currencyCode": payload.get("from_currency", ""),
                    "toCurrency": payload.get("to_currency", ""),
                    "amount": f'{round(float(payload.get("amount", 1)), 2)}',
                })
            elif super().get_bank_id() == super().COOP:
                data.update({
                    "MessageReference": payload.get("reference", get_code(length=20)),
                    "FromCurrencyCode": payload.get("from_currency", ""),
                    "ToCurrencyCode": payload.get("to_currency", "")
                })

        data.update(payload.get("additional_properties", {}))

        return data

    def get_full_statement_transaction_dict(self):
        return self.full_statement_transaction_dict

    def response(self):

        data = {}

        response_data = super().response()

        try:

            if super().get_operation() == super().BALANCE:

                data.update({
                    "message": "",
                    "code": "-111111",
                    "balance": "0",
                    "balance_time": "",
                    "account_type": "",
                    "cleared_balance": "0",
                    "booked_balance": "0",
                    "blocked_balance": "0",
                    "arrears_amount": "0",
                    "branch_name": "",
                    "branch_code": "",
                    "average_balance": "0",
                    "uncleared_balance": "0",
                    "over_draft_limit": "0",
                    "credit_limit": "0",
                })

                if super().get_bank_id() == super().COOP:

                    data["message"] = response_data.get("MessageDescription", "")
                    data["code"] = f'{response_data.get("MessageCode", "-111111")}'
                    data["balance"] = f'{response_data.get("AvailableBalance", "0")}'
                    data["balance_time"] = response_data.get("MessageDateTime", "")

                    data["account_type"] = response_data.get("ProductName", "")
                    data["cleared_balance"] = f'{response_data.get("ClearedBalance", "0")}'
                    data["booked_balance"] = f'{response_data.get("BookedBalance", "0")}'
                    data["blocked_balance"] = f'{response_data.get("BlockedBalance", "0")}'
                    data["arrears_amount"] = f'{response_data.get("ArrearsAmount", "0")}'
                    data["branch_name"] = response_data.get("BranchName", "")
                    data["branch_code"] = response_data.get("BranchSortCode", "")
                    data["average_balance"] = f'{response_data.get("AverageBalance", "0")}'
                    data["uncleared_balance"] = f'{response_data.get("UnclearedBalance", "0")}'
                    data["over_draft_limit"] = f'{response_data.get("ODLimit", "0")}'
                    data["credit_limit"] = f'{response_data.get("CreditLimit", "0")}'

                elif super().get_bank_id() == super().EQUITY:

                    data["message"] = response_data.get("message", "")
                    data["code"] = f'{response_data.get("code", "-111111")}'
                    data["balance_time"] = response_data.get("response_time", "")

                    data["balance"] = "0"

                    balances = response_data.get("data", {}).get("balances", [])
                    if bool(balances):
                        if balances[0].get('type', '') == 'Available':
                            data["balance"] = f'{balances[0].get("amount", "0")}'
                        if balances[1].get('type', '') == 'Current':
                            data["cleared_balance"] = f'{balances[1].get("amount", "0")}'
                # If bank_id is UBA
                elif super().get_bank_id() == super().UBA:

                    data["message"] = ''
                    data["code"] = f'{int(float(response_data.get("sendTransactionResponse", {}).get("return", {}).get("C24TRANRES", {}).get("ACTION_CODE", "-111111")))}'
                    data["balance"] = f'{float(response_data.get("sendTransactionResponse", {}).get("return", {}).get("C24TRANRES", {}).get("AVAILABLE_BALANCE", "0"))}'
                    data["balance_time"] = datetime.strptime(f'{response_data.get("sendTransactionResponse", {}).get("return", {}).get("C24TRANRES", {}).get("TRAN_DATE_TIME",)}', '%Y%d%m%H%M%S').strftime('%Y-%m-%d %H:%M:%S')
                    if int(data["code"]):
                        data["message"] = "Transaction Failed"
                    else:
                        data["message"] = "Success"

            elif super().get_operation() == super().MINI_STATEMENT or super().get_operation() == super().ACCOUNT_TRANSACTIONS:

                if super().get_bank_id() == super().COOP:

                    data["message"] = response_data.get("MessageDescription", "")
                    data["code"] = f'{response_data.get("MessageCode", "-111111")}'
                    data["transactions"] = []
                    data["transactions_count"] = f'{len(response_data.get("Transactions", []))}'

                    transactions = response_data.get("Transactions", [])

                    for i in range(len(transactions)):
                        transaction = {
                            "currency_code": "KES",
                            "date": transactions[i].get("TransactionDate", ""),
                            "description": transactions[i].get("Narration", ""),
                            "reference": transactions[i].get("TransactionReference", "")
                        }

                        if transactions[i].get("TransactionType", "") == "D":
                            transaction["amount"] = f'{transactions[i].get("DebitAmount", "0")}'
                            transaction["type"] = "Debit"

                        elif transactions[i].get("TransactionType", "") == "C":
                            transaction["amount"] = f'{transactions[i].get("CreditAmount", "0")}'
                            transaction["type"] = "Credit"

                        data["transactions"].append(transaction)

                if super().get_operation() == super().MINI_STATEMENT:

                    if super().get_bank_id() == super().EQUITY:

                        data["message"] = response_data.get("message", "")
                        data["code"] = f'{response_data.get("code", "-111111")}'
                        data["transactions"] = []
                        data["transactions_count"] = f'{len(response_data.get("data", {}).get("transactions", []))}'

                        transactions = response_data.get(
                            "data", {}).get("transactions", [])

                        for i in range(len(transactions)):

                            transaction = {
                                "currency_code": response_data.get("data", {}).get("currency", "KES"),
                                "date": datetime.fromisoformat(
                                    transactions[i].get(
                                        "date", "").replace(" ","") + '+00:00'
                                ).strftime('%Y-%m-%d %H:%M:%S'),
                                "description": transactions[i].get("description", ""),
                                "amount":  f'{transactions[i].get("amount", "0")}',
                                "type":  transactions[i].get("type", "")
                            }

                            data["transactions"].append(transaction)

            elif super().get_operation() == super().ACCOUNT_VALIDATION:

                if super().get_bank_id() == super().COOP:

                    data["message"] = response_data.get("MessageDescription", "")
                    data["code"] = f'{response_data.get("MessageCode", "-111111")}'
                    data["account_name"] = ""

                elif super().get_bank_id() == super().EQUITY:

                    data["message"] = response_data.get("message", "")
                    data["code"] = f'{response_data.get("code", "-111111")}'
                    data["account_name"] = ""
                    customer = response_data.get("data", {}).get("customer", [])
                    if len(customer) > 0:
                        data["account_name"] = customer[0].get("name", "")

                # If bank_id is DTB
                elif super().get_bank_id() == super().DTB:
                    if isinstance(response_data, list):
                        data["message"] = response_data[0]
                        data["code"] = '-111111'
                        data["account_name"] = ""
                    else:
                        data["message"] = response_data.get(
                            "content", {}).get("account_description", "")
                        data["code"] = '0'
                        data["account_name"] = response_data.get(
                            "content", {}).get("customer_name", "")

            elif super().get_operation() == super().FULL_STATEMENT:

                if super().get_bank_id() == super().COOP:

                    data["message"] = response_data.get("MessageDescription", "")
                    data["code"] = f'{response_data.get("MessageCode", "-111111")}'
                    data["statement_time"] = response_data.get(
                        "MessageDateTime", "")
                    data["statement_reference"] = response_data.get(
                        "MessageReference", "")
                    data["transactions_count"] = f'{len(response_data.get("Transactions", []))}'
                    data["transactions"] = []

                    transactions = response_data.get("Transactions", [])

                    for i in range(len(transactions)):
                        transaction={}
                        transaction.update(self.get_full_statement_transaction_dict())

                        # the reference below is a callback reference sent with the fullstatememt
                        # if the fullstatement sent is one that relates to a callback reference
                        if 'nash_reference' in transactions[i].keys():
                            transaction['nash_reference']=transactions[i].get("nash_reference")

                        transaction.update(
                            {
                                "currency_code": "KES",
                                "date": transactions[i].get("TransactionDate", ""),
                                "description": transactions[i].get("Narration", ""),
                                "transaction_id": transactions[i].get("TransactionID", transactions[i].get("TransactionId", "")),
                                "value_date": transactions[i].get("ValueDate", ""),
                                "service_point": transactions[i].get("ServicePoint", ""),
                                "running_cleared_balance": f'{transactions[i].get("RunningClearedBalance", "0")}',
                                "debit_limit": f'{float(transactions[i].get("DebitLimit", "0"))}',
                                "limit_expiry_date": transactions[i].get("LimitExpiryDate", ""),
                            }
                        )

                        if transactions[i].get("TransactionType", "") == "D":
                            transaction["amount"] = f'{transactions[i].get("DebitAmount", "0")}'
                            transaction["type"] = "Debit"

                        elif transactions[i].get("TransactionType", "") == "C":
                            transaction["amount"] = f'{transactions[i].get("CreditAmount", "0")}'
                            transaction["type"] = "Credit"

                        transaction["reference"] = transactions[i].get(
                            "TransactionReference", "")
                        transaction["running_balance"] = f'{transactions[i].get("RunningBookBalance", "0")}'

                        data["transactions"].append(transaction)

                elif super().get_bank_id() == super().EQUITY:

                    # This is implemented since equity sometimes sends data as a truncated JSON String 
                    try:
                        if isinstance(response_data, str):
                            # get the JOSN response and complete the JSON String by appending the missing closing brackets
                            response_data = '{}{}'.format(response_data, '"}]}}')
                            # convert the completed JSON String to JSON
                            response_data = json.loads(response_data)
                    except Exception as e:
                        data['error'] = str(e)

                    if isinstance(response_data, dict):
                        data["message"] = response_data.get("message", "")
                        data["code"] = f'{response_data.get("code", "-111111")}'
                        data["statement_time"] = response_data.get(
                            "response_time", "")
                        data["statement_reference"] = response_data.get("statement_reference", "")
                        data["transactions_count"] = f'{len(response_data.get("data", {}).get("transactions", []))}'
                        data["transactions"] = []

                        transactions = response_data.get("data", {}).get("transactions", [])

                        for i in range(len(transactions)):
                            transaction={}
                            transaction.update(self.get_full_statement_transaction_dict())

                            # the reference below is a callback reference sent with the fullstatememt
                            # if the fullstatement sent is one that relates to a callback reference
                            if 'nash_reference' in transactions[i].keys():
                                transaction['nash_reference']=transactions[i].get("nash_reference")

                            transaction.update({
                                "currency_code": response_data.get("data", {}).get("currency", "KES"),
                                "date": datetime.fromisoformat(
                                    transactions[i].get(
                                        "date", "") + '+00:00'
                                ).strftime('%Y-%m-%d %H:%M:%S'),
                                "description": transactions[i].get("description", ""),
                                "amount":  f'{transactions[i].get("amount", "0")}',
                                "type":  transactions[i].get("type", ""),
                                "serial":  transactions[i].get("serial", ""),
                                "reference":  transactions[i].get("reference", ""),
                                "running_balance":  f'{transactions[i].get("runningBalance", {}).get("amount", "0")}',
                                "posted_date": datetime.fromisoformat(
                                    transactions[i].get(
                                        "postedDateTime", "") + '+00:00'
                                ).strftime('%Y-%m-%d %H:%M:%S'),
                            })

                            data["transactions"].append(transaction)
                    else:
                        data['response'] = response_data

                # If bank_id is UBA
                elif super().get_bank_id() == super().UBA:

                    data["message"] = ''
                    data["code"] = f'{int(float(response_data.get("sendTransactionResponse", {}).get("return", {}).get("C24TRANRES", {}).get("ACTION_CODE", "-111111")))}'
                    data["statement_reference"] = f'{response_data.get("sendTransactionResponse", {}).get("return", {}).get("C24TRANRES", {}).get("STAN", "")}'
                    if int(data["code"]):
                        data["message"] = "Transaction Failed"
                    else:
                        data["message"] = "Success"
                    data["transactions"] = []

                    transactions = response_data.get("sendTransactionResponse", {}).get("return", {}).get(
                        "C24TRANRES", {}).get("TRANS_INFO", {}).get("TRAN", {}).get("element", [])
                    data["transactions_count"] = f'{len(transactions)}'

                    for i in range(len(transactions)):
                        transaction={}
                        transaction.update(self.get_full_statement_transaction_dict())

                        transaction.update({
                            "currency_code": response_data.get("sendTransactionResponse", {}).get(
                                "return", {}).get("C24TRANRES", {}).get("BALANCE_CURRENCY", "NGN"),
                            "date": datetime.strptime(f'{transactions[i].get("TRAN_DATE", None)}', '%Y%d%m').strftime('%Y-%m-%d'),

                            "description": transactions[i].get("NARRATION", ""),
                            "amount": f'{transactions[i].get("TRAN_AMT", "0")}',
                            "running_balance": f'{transactions[i].get("BALANCE", "0")}',

                            "transaction_id": transactions[i].get("TRAN_ID", ""),
                            "serial": f'{transactions[i].get("TRAN_SNUM", "")}',
                            "value_date": datetime.strptime(f'{transactions[i].get("VALUE_DATE", None)}', '%Y%d%m').strftime('%Y-%m-%d'),
                            "posted_date": datetime.strptime(f'{transactions[i].get("DATE_POSTED", None)}', '%Y%d%m%H%M%S').strftime('%Y-%m-%d %H:%M:%S'),
                        })

                        if transactions[i].get("PART_TRAN_TYPE", "") == "D":
                            transaction["type"] = "Debit"
                        elif transactions[i].get("PART_TRAN_TYPE", "") == "C":
                            transaction["type"] = "Credit"

                        if transactions[i].get("REF_NUM", {}).get("@null", "true") == "true":
                            transaction["reference"] = ""

                        data["transactions"].append(transaction)

            elif super().get_operation() == super().PDF_TO_JSON or super().get_operation() == super().GET_JSON_PDF:
                data = self.standardize_pdf_to_json(response_data=response_data)

            elif super().get_operation() == super().FOREX_RATE:
                data["code"] = "-111111"
                data['message'] = response_data
                if isinstance(response_data, dict):                    
                    if super().get_bank_id() == super().EQUITY:
                        data["message"] = response_data.get("message", "")
                        data["code"] = f'{response_data.get("code", "-111111")}'
                        data['rate'] = f'{response_data.get("data", {}).get("rate", "-1")}'
                        data['rate_type'] = f'{response_data.get("data", {}).get("rateCode", "")}'
                    elif super().get_bank_id() == super().COOP:
                        data["message"] = response_data.get("MessageDescription", "")
                        data["code"] = f'{response_data.get("MessageCode", "-111111")}'
                        data['rate'] = f'{response_data.get("Rate", "-1")}'
                        data['rate_type'] = f'{response_data.get("RateType", "")}'
                        if data["code"] == 'S_001':
                            data["code"] = "0"
                        else:
                            data["code"] = "-111111"
                            data['message'] = response_data                    

            elif super().get_operation() == super().JOBS_ACCOUNT_BALANCES:
                data = []
                if super().get_bank_id() == super().COOP:
                    for account_balance_data in response_data.get('data', []):
                        data.append({
                            "status": f'{account_balance_data.get("status", "-1")}',
                            "created_at": account_balance_data.get("created_at", ''),
                            "available_balance": f'{account_balance_data.get("account_balance_response", {}).get("AvailableBalance", "0")}',
                        })

                        if account_balance_data.get("status", -1) != 0:
                            data["available_balance_error"] = account_balance_data.get(
                                'account_balance_response', {})

            elif super().get_operation() == super().JOBS_ACCOUNT_STATEMENT:
                data = []
                if super().get_bank_id() == super().COOP:

                    for account_statement_data in response_data.get('data', []):
                        data.append({
                            "status": account_statement_data.get("status", -1),
                            "created_at": account_statement_data.get("created_at", ''),
                            "transactions": [],
                        })

                        if account_statement_data.get("status", -1) != 0:
                            data[-1]["transaction_error"] = account_statement_data.get(
                                'account_statement_response', {})

                        else:
                            transactions_data = account_statement_data.get(
                                'account_statement_response', {}).get("Transactions", [])
                            for transaction in transactions_data:
                                transaction_data = {
                                    "date": transaction.get("TransactionDate", ''),
                                    "description": transaction.get("Narration", ''),
                                    "reference": transaction.get("TransactionReference", ''),
                                }

                                if transaction.get("TransactionType", "") == "D":
                                    transaction_data["amount"] = f'{transaction.get("DebitAmount", "0")}'
                                    transaction_data["type"] = "Debit"

                                elif transaction.get("TransactionType", "") == "C":
                                    transaction_data["amount"] = f'{transaction.get("CreditAmount", "0")}'
                                    transaction_data["type"] = "Credit"

                                data[-1].get("transactions", []
                                            ).append(transaction_data)

            if bool(data):
                if isinstance(data, dict):
                    if 'transactions' in data.keys() and 'code' in data.keys():
                        if len(data["transactions"]) == 0 and int(data["code"]) == "-111111":
                            data['error'] = response_data
                return data
            if super().get_bank_id() in super().THIRD_PARTY_BANKING.keys():
                return response_data
        except Exception as e:
            data['code']="-111111"
            data['sync_error']=str(e)
            data['bank_core_response']=response_data
            return data

        return response_data
