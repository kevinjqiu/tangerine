import json
import logging
import datetime
import subprocess
from tangerine import TangerineClient, DictionaryBasedSecretProvider
from tangerine.exceptions import UnsupportedAccountTypeForDownload


FROM = datetime.date(2017, 6, 1)
TO = datetime.date(2017, 11, 2)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    output = subprocess.check_output(['gpg', '-d', 'tangerine.json.gpg'])
    secret_provider = DictionaryBasedSecretProvider(json.loads(output))
    client = TangerineClient(secret_provider)
    with client.login():
        accounts = [
            acct for acct in client.list_accounts()
            if acct['type'] != 'CREDIT_CARD'
        ]
        for acct in accounts:
            try:
                client.download_ofx(acct, FROM, TO)
            except UnsupportedAccountTypeForDownload as e:
                print(e)
