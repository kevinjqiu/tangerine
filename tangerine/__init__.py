"""tangerine - API for the Tangerine Bank"""
import os

__version__ = open(os.path.join(os.path.dirname(__file__), 'VERSION')).read()
__author__ = 'Kevin J. Qiu <kevin@idempotent.ca>'


from .client import TangerineClient  # noqa
from .secret_provider import SecretProvider  # noqa
from .secret_provider import InteractiveSecretProvider  # noqa
from .secret_provider import DictionaryBasedSecretProvider  # noqa
