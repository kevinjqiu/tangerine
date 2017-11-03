import datetime
import json
import logging
import subprocess
from tangerine import TangerineClient, DictionaryBasedSecretProvider


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    output = subprocess.check_output(['gpg', '-d', 'tangerine.json.gpg'])
    secret_provider = DictionaryBasedSecretProvider(json.loads(output))
    client = TangerineClient(secret_provider)
    with client.login():
        cc_accounts = [
            acct for acct in client.list_accounts()
            if acct['type'] == 'CREDIT_CARD'
        ]

        for acct in cc_accounts:
            acct_details = client.get_account(acct['number'])
            billing_cycles = acct_details['credit_card']['cc_account_details']['card_details']['billing_cycle_ranges']
            for cycle in billing_cycles:
                start_date, end_date = cycle['start_date'], cycle['end_date']
                start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
                client.download_ofx(acct, start_date, end_date)
