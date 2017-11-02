from urllib.parse import urlencode
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


class TangerineClient(object):
    def __init__(self, secret_provider, session=None, locale=DEFAULT_LOCALE):
        if session is None:
            session = requests.Session()
        self.session = session
        self.login_flow = TangerineLoginFlow(secret_provider, self.session, locale)

    @staticmethod
    def _api(path):
        return 'https://secure.tangerine.ca/web/rest{}'.format(path)

    @contextlib.contextmanager
    def login(self):
        self.login_flow.start()
        try:
            yield
        except:
            raise
        finally:
            self.login_flow.end()

    def me(self):
        r = self.session.get(self._api('/v1/customers/my'))
        return r.json()

    def accounts(self):
        r = self.session.get(self._api('/pfm/v1/accounts'))
        return r.json()

    def transactions(self, account_ids, period_from, period_to):
        # datetime format: 2017-10-03T00:00:00.000Z
        params = {
            'accountIdentifiers': ','.join(account_ids),
            'hideAuthorizedStatus': True,
            'periodFrom': period_from,
            'periodTo': period_to,
            'skip': 0,
        }
        r = self.session.get(self._api('/pfm/v1/transactions?{}'.format(urlencode(params))))
        return r.json()

    def get_transaction_download_token(self):
        r = self.session.get(self._api('/v1/customers/my/security/transaction-download-token'))
        return r.json()['token']

    def download_ofx(self, account, start_date, end_date):
        token = self.get_transaction_download_token()
        file_name = 'transactions.qfx'
        params = {
            'fileType': 'OFX',
            'ofxVersion': '102',
            'sessionId': 'tng',
            'orgName': 'Tangerine',
            'bankId': '0614',
            'language': 'eng',
            'acctType': account['type'],
            'acctNum': account['display_name'],
            'acctName': account['nickname'],
            'userDefined': token,
            'startDate': start_date,
            'endDate': end_date,
            'orgId': 10951,
            'custom.tag': 'customValue',
            'csvheader': 'Date,Transaction,Name,Memo,Amount',
        }
        response = self.session.get('https://ofx.tangerine.ca/{}?{}'.format(file_name, urlencode(params)))
        response.raise_for_status()
        return response.text
