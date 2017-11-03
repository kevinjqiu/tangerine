from urllib.parse import urlencode, quote
from . import exceptions
import functools
import datetime
import contextlib
import requests
import logging


DEFAULT_LOCALE = 'en_CA'


class TangerineLoginFlow(object):
    def __init__(self, secret_provider, session, locale):
        self.secret_provider = secret_provider
        self.session = session
        self.locale = locale

    @staticmethod
    def _init_tangerine_url(**kvs):
        return 'https://secure.tangerine.ca/web/InitialTangerine.html?{}'.format(urlencode(kvs))

    @staticmethod
    def _tangerine_url(**kvs):
        if kvs:
            return 'https://secure.tangerine.ca/web/Tangerine.html?{}'.format(urlencode(kvs))
        else:
            return 'https://secure.tangerine.ca/web/Tangerine.html'

    def _get_init_tangerine(self, command):
        resp = self.session.get(self._init_tangerine_url(command=command, device='web', locale=self.locale),
                                headers={'x-web-flavour': 'fbe'})
        resp.raise_for_status()
        logging.debug(resp.text)
        return resp

    def _post_tangerine(self, data):
        data = dict(data)
        data.update({
            'locale': self.locale,
            'device': 'web',
        })
        resp = self.session.post(
            self._tangerine_url(),
            headers={
                'x-web-flavour': 'fbe',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Accept': 'application/json',
            },
            data=data)
        resp.raise_for_status()
        logging.debug(resp.text)
        return resp

    def _get_tangerine(self, **kv):
        resp = self.session.get(self._tangerine_url(**kv),
                                headers={'x-web-flavour': 'fbe', 'Accept': 'application/json'})
        resp.raise_for_status()
        logging.debug(resp.text)
        return resp

    def _get_pin_phrase(self):
        r = self._get_tangerine(command='displayPIN')
        return r.json()['MessageBody']['Phrase']

    def _get_security_challenge(self):
        r = self._get_tangerine(command='displayChallengeQuestion')
        return r.json()['MessageBody']['Question']

    def end(self):
        logging.info('Logging out...')
        self._get_init_tangerine('displayLogout')

    def start(self):
        logging.info('Initiating Tangerine logging flow')
        self._get_init_tangerine('displayLogout')
        self._get_init_tangerine('displayLoginRegular')

        self._post_tangerine(data={
            'command': 'PersonalCIF',
            'ACN': self.secret_provider.get_username(),
        })

        question = self._get_security_challenge()
        answer = self.secret_provider.get_security_challenge_answer(question)

        self._post_tangerine(data={
            'command': 'verifyChallengeQuestion',
            'BUTTON': 'Next',
            'Answer': answer,
            'Next': 'Next',
        })

        phrase = self._get_pin_phrase()
        self._post_tangerine(data={
            'locale': self.locale,
            'command': 'validatePINCommand',
            'BUTTON': 'Go',
            'PIN': self.secret_provider.get_password(phrase),
            'Go': 'Next',
            'callSource': '4',
        })

        self._get_tangerine(command='PINPADPersonal')
        self._get_tangerine(command='displayAccountSummary', fill=1)


def api_response(root_key=''):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            response_json = fn(*args, **kwargs)
            if response_json['response_status']['status_code'] != 'SUCCESS':
                raise exceptions.APIResponseError(response_json)
            if not root_key:
                return response_json
            return response_json[root_key]
        return wrapper
    return decorator


class TangerineClient(object):
    def __init__(self, secret_provider, session=None, locale=DEFAULT_LOCALE):
        if session is None:
            session = requests.Session()
        self.session = session
        self.login_flow = TangerineLoginFlow(secret_provider, self.session, locale)

    def _api_get(self, path):
        url = 'https://secure.tangerine.ca/web/rest{}'.format(path)
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    @contextlib.contextmanager
    def login(self):
        self.login_flow.start()
        try:
            yield
        except:
            raise
        finally:
            self.login_flow.end()

    @api_response('customer')
    def me(self):
        return self._api_get('/v1/customers/my')

    @api_response('accounts')
    def list_accounts(self):
        return self._api_get('/pfm/v1/accounts')

    @api_response('account_summary')
    def get_account(self, account_id: str):
        return self._api_get('/v1/accounts/{}?billing-cycle-ranges=true'.format(account_id))

    @api_response('transactions')
    def list_transactions(self, account_ids: list, period_from: datetime.date, period_to: datetime.date):
        params = {
            'accountIdentifiers': ','.join(account_ids),
            'hideAuthorizedStatus': True,
            'periodFrom': period_from.strftime('%Y-%m-%dT00:00:00.000Z'),
            'periodTo': period_to.strftime('%Y-%m-%dT00:00:00.000Z'),
            'skip': 0,
        }
        return self._api_get('/pfm/v1/transactions?{}'.format(urlencode(params)))

    def _get_transaction_download_token(self):
        return self._api_get('/v1/customers/my/security/transaction-download-token')['token']

    def download_ofx(self, account, start_date: datetime.date, end_date: datetime.date):
        if account['type'] == 'CHEQUING':
            account_type = 'SAVINGS'
            account_display_name = account['display_name']
            account_nickname = account['nickname']
        elif account['type'] == 'SAVINGS':
            account_type = 'SAVINGS'
            account_display_name = account['display_name']
            account_nickname = account['nickname']
        elif account['type'] == 'CREDIT_CARD':
            account_type = 'CREDITLINE'
            account_details = self.get_account(account['number'])['account_summary']
            account_display_name = account_details['display_name']
            account_nickname = account_details['account_nick_name']
        else:
            raise exceptions.UnsupportedAccountTypeForDownload(account['type'])

        token = self._get_transaction_download_token()
        file_name = '{}.QFX'.format(account_nickname)
        params = {
            'fileType': 'QFX',
            'ofxVersion': '102',
            'sessionId': 'tng',
            'orgName': 'Tangerine',
            'bankId': '0614',
            'language': 'eng',
            'acctType': account_type,
            'acctNum': account_display_name,
            'acctName': account_nickname,
            'userDefined': token,
            'startDate': start_date.strftime('%Y%m%d'),
            'endDate': end_date.strftime('%Y%m%d'),
            'orgId': 10951,
            'custom.tag': 'customValue',
            'csvheader': 'Date,Transaction,Name,Memo,Amount',
        }
        response = self.session.get('https://ofx.tangerine.ca/{}?{}'.format(quote(file_name), urlencode(params)),
                                    headers={'Referer': 'https://www.tangerine.ca/app/'})
        response.raise_for_status()
        return response.text
