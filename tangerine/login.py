from urllib.parse import urlencode
import logging


logger = logging.getLogger(__name__)


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
        logger.debug(resp.text)
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
        logger.debug(resp.text)
        return resp

    def _get_tangerine(self, **kv):
        resp = self.session.get(self._tangerine_url(**kv),
                                headers={'x-web-flavour': 'fbe', 'Accept': 'application/json'})
        resp.raise_for_status()
        logger.debug(resp.text)
        return resp

    def _get_pin_phrase(self):
        r = self._get_tangerine(command='displayPIN')
        return r.json()['MessageBody']['Phrase']

    def _get_security_challenge(self):
        r = self._get_tangerine(command='displayChallengeQuestion')
        return r.json()['MessageBody']['Question']

    def end(self):
        logger.info('Logging out...')
        self._get_init_tangerine('displayLogout')

    def start(self):
        logger.info('Initiating Tangerine logging flow')
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
