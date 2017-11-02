from urllib.parse import urlencode
import requests


class TangerineScraper(object):
    def __init__(self, secret_provider, session=None):
        if session is None:
            session = requests.Session()
        self.session = session
        self.secret_provider = secret_provider

    @staticmethod
    def _init_tangerine(**kvs):
        return 'https://secure.tangerine.ca/web/InitialTangerine.html?{}'.format(urlencode(kvs))

    @staticmethod
    def _tangerine(**kvs):
        if kvs:
            return 'https://secure.tangerine.ca/web/Tangerine.html?{}'.format(urlencode(kvs))
        else:
            return 'https://secure.tangerine.ca/web/Tangerine.html'

    @staticmethod
    def _api(path):
        return 'https://secure.tangerine.ca/web/rest{}'.format(path)

    def my_account(self):
        r = self.session.get(self._api('/v1/customers/my'))
        return r.json()

    def logout(self):
        self.session.get(self._init_tangerine(command='displayLogout', device='web', locale='en_CA'),
                         headers={'x-web-flavour': 'fbe'})

    def login(self):
        self.logout()
        self.session.get(self._init_tangerine(command='displayLoginRegular', device='web', locale='en_CA',
                         headers={'x-web-flavour': 'fbe'}))

        r = self.session.post(
            self._tangerine(),
            headers={
                'x-web-flavour': 'fbe',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            },
            data={
                'command': 'PersonalCIF',
                'locale': 'en_CA',
                'device': 'web',
                'ACN': self.secret_provider.get_username(),
            })
        r.raise_for_status()

        r = self.session.get(self._tangerine(command='displayChallengeQuestion'), headers={'x-web-flavour': 'fbe'})
        r.raise_for_status()

        question = r.json()['MessageBody']['Question']
        answer = self.secret_provider.get_security_challenge_answer(question)

        r = self.session.post(
            self._tangerine(),
            headers={
                'x-web-flavour': 'fbe',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            },
            data={
                'command': 'verifyChallengeQuestion',
                'BUTTON': 'Next',
                'Answer': answer,
                'Next': 'Next',
            })
        r.raise_for_status()

        r = self.session.post(
            self._tangerine(),
            headers={
                'x-web-flavour': 'fbe',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Accept': 'application/json',
            },
            data={
                'locale': 'en_CA',
                'command': 'validatePINCommand',
                'BUTTON': 'Go',
                'PIN': self.secret_provider.get_password(),
                'Go': 'Next',
                'callSource': '4',
            })
        print(r.text)
        r = self.session.get(self._tangerine(command='PINPADPersonal'))
        print(r.text)
