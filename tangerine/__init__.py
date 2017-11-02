"""tangerine - API for the Tangerine Bank"""

__version__ = '0.1.0'
__author__ = 'Kevin J. Qiu <kevin@idempotent.ca>'
__all__ = []


from .tangerine import TangerineClient  # noqa
from .secret_provider import SecretProvider, InteractiveSecretProvider  # noqa
