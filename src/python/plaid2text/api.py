import plaid
from plaid.api import plaid_api

def new_plaid_api_client(client_id: str, secret: str) -> plaid_api.PlaidApi:
    configuration = plaid.Configuration(
        host=plaid.Environment.Production,
        api_key = {
            'clientId': client_id,
            'secret': secret,
            'plaidVersion': '2020-09-14',
        }
    )
    api_client = plaid.ApiClient(configuration)
    return plaid_api.PlaidApi(api_client)