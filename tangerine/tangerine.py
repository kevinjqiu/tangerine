from urllib.parse import urlencode
import contextlib
import requests


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
        return self.session.get(self._init_tangerine_url(command=command, device='web', locale=self.locale),
                                headers={'x-web-flavour': 'fbe'})

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
        return resp

    def _get_tangerine(self, **kv):
        r = self.session.get(self._tangerine_url(**kv),
                             headers={'x-web-flavour': 'fbe', 'Accept': 'application/json'})
        r.raise_for_status()
        return r

    def end(self):
        self._get_init_tangerine('displayLogout')

    def start(self):
        self._get_init_tangerine('displayLogout')
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
        print(r.text)


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

    def my_account(self):
        r = self.session.get(self._api('/v1/customers/my'))
        return r.json()
