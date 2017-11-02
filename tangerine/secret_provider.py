import abc
import getpass


class SecretProvider(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_username(self):
        pass

    @abc.abstractmethod
    def get_password(self):
        pass

    @abc.abstractmethod
    def get_security_challenge_answer(self, challenge):
        pass


class InteractiveSecretProvider(SecretProvider):
    def get_username(self):
        return input('Username: ')

    def get_password(self):
        return getpass.getpass('PIN: ')

    def get_security_challenge_answer(self, challenge):
        print('Security challenge: {}'.format(challenge))
        return input('Answer: ')
