import abc
import getpass


class SecretProvider(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_username(self):
        """Get the username/account number"""

    @abc.abstractmethod
    def get_password(self, phrase: str):
        """Get the password/PIN for the user"""

    @abc.abstractmethod
    def get_security_challenge_answer(self, challenge: str):
        """Get the answer to the security challenge"""


class InteractiveSecretProvider(SecretProvider):
    def __init__(self, input=input, getpass=getpass.getpass):
        self.input = input
        self.getpass = getpass

    def get_username(self):
        return self.input('Username: ')

    def get_password(self, phrase: str):
        print('Phrase: {}'.format(phrase))
        return self.getpass('PIN: ')

    def get_security_challenge_answer(self, challenge: str):
        print('Security challenge: {}'.format(challenge))
        return self.input('Answer: ')
