from urllib.parse import urlencode
import requests


DEFAULT_LOCALE = 'en_CA'


class TangerineClient(object):
    def __init__(self, secret_provider, session=None, locale=DEFAULT_LOCALE):
        if session is None:
            session = requests.Session()
        self.session = session
        self.secret_provider = secret_provider
        self.locale = locale

    @staticmethod
    def _init_tangerine_url(**kvs):
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

    def _get_init_tangerine(self, command):
        return self.session.get(self._init_tangerine_url(command=command, device='web', locale=self.locale),
                                headers={'x-web-flavour': 'fbe'})

    def _post_tangerine(self, data):
        data = dict(data)
        data.update({
            'locale': self.locale,
            'device': 'web',
        })
        resp = self.session.post(
            self._tangerine(),
            headers={
                'x-web-flavour': 'fbe',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Accept': 'application/json',
            },
            data=data)
        resp.raise_for_status()
        return resp

    def _get_tangerine(self, **kv):
        r = self.session.get(self._tangerine(**kv),
                             headers={'x-web-flavour': 'fbe', 'Accept': 'application/json'})
        r.raise_for_status()
        return r

    def my_account(self):
        r = self.session.get(self._api('/v1/customers/my'))
        return r.json()

    def logout(self):
        self._get_init_tangerine('displayLogout')

    def login(self):
        self.logout()
        self._get_init_tangerine('displayLoginRegular')

        self._post_tangerine(data={
            'command': 'PersonalCIF',
            'ACN': self.secret_provider.get_username(),
        })

        r = self._get_tangerine(command='displayChallengeQuestion')
        question = r.json()['MessageBody']['Question']
        answer = self.secret_provider.get_security_challenge_answer(question)

        r = self._post_tangerine(data={
            'command': 'verifyChallengeQuestion',
            'BUTTON': 'Next',
            'Answer': answer,
            'Next': 'Next',
        })

        r = self._post_tangerine(data={
            'locale': self.locale,
            'command': 'validatePINCommand',
            'BUTTON': 'Go',
            'PIN': self.secret_provider.get_password(),
            'Go': 'Next',
            'callSource': '4',
        })

        print(r.text)
        r = self._get_tangerine(command='PINPADPersonal')
        print(r.text)
        r = self._get_tangerine(command='displayAccountSummary', fill=1)
        # r = self.session.get('https://secure.tangerine.ca/web/Tangerine.html?command=displayAccountSummary&fill=1')
        print(r.text)
