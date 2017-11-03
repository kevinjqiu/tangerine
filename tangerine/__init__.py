"""tangerine - API for the Tangerine Bank"""

__version__ = '0.1.0'
__author__ = 'Kevin J. Qiu <kevin@idempotent.ca>'


from .client import TangerineClient  # noqa
from .secret_provider import SecretProvider  # noqa
from .secret_provider import InteractiveSecretProvider  # noqa
from .secret_provider import DictionaryBasedSecretProvider  # noqa
