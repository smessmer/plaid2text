#! /usr/bin/env python3

from collections import OrderedDict
import datetime
import os
import sys
import textwrap

from plaid2text.api import new_plaid_api_client

import plaid
from plaid.exceptions import ApiException
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from plaid.model.transactions_get_request import TransactionsGetRequest

import plaid2text.config_manager as cm
from plaid2text.interact import prompt, clear_screen, NullValidator
from plaid2text.interact import NumberValidator, NumLengthValidator, YesNoValidator, PATH_COMPLETER


class PlaidAccess():
    def __init__(self, client_id=None, secret=None):
        if client_id and secret:
            self.client_id = client_id
            self.secret = secret
        else:
            self.client_id, self.secret = cm.get_plaid_config()

        self.client = new_plaid_api_client(self.client_id, self.secret)

    def get_transactions(self,
                         access_token,
                         start_date,
                         end_date,
                         account_ids):
        """Get transaction for a given account for the given dates"""

        ret = []
        total_transactions = None
        page = 0
        account_array = []
        account_array.append(account_ids)
        while True:
            page += 1 
            if total_transactions:
                print("Fetching page %d, already fetched %d/%d transactions" % ( page, len(ret), total_transactions))
            else:
                print("Fetching page 1")

            try:
                options = TransactionsGetRequestOptions()
                options.offset = len(ret)
                options.account_ids=account_array
                request = TransactionsGetRequest(
                    access_token=access_token,
                    start_date=start_date.date(),
                    end_date=end_date.date(),
                    options=options,
                )
                response = self.client.transactions_get(request)
            except ApiException as ex:
                print("Unable to update plaid account [%s] due to: " % account_ids, file=sys.stderr)
                print("    %s" % ex, file=sys.stderr )
                sys.exit(1)

            total_transactions = response['total_transactions']

            ret.extend(response['transactions'])

            if len(ret) >= total_transactions: break

        print("Downloaded %d transactions for %s - %s" % ( len(ret), start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))

        return ret
