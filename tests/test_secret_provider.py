import mock
from pytest import fixture
from tangerine import InteractiveSecretProvider


@fixture
def interactive_secret_provider():
    return InteractiveSecretProvider(input=mock.Mock(), getpass=mock.Mock())


def test_interactive_secret_provider___get_username(interactive_secret_provider):
    interactive_secret_provider.input.return_value = 'USER'
    assert 'USER' == interactive_secret_provider.get_username()
    assert [mock.call('Username: ')] == interactive_secret_provider.input.call_args_list


def test_interactive_secret_provider___get_password(interactive_secret_provider):
    interactive_secret_provider.getpass.return_value = 'PASSWORD'
    assert 'PASSWORD' == interactive_secret_provider.get_password('PHRASE')
    assert [mock.call('PIN: ')] == interactive_secret_provider.getpass.call_args_list
    assert [] == interactive_secret_provider.input.call_args_list


def test_interactive_secret_provider___get_security_challenge_answer(interactive_secret_provider):
    interactive_secret_provider.input.return_value = 'ANSWER'
    assert 'ANSWER' == interactive_secret_provider.get_security_challenge_answer('QUESTION')
    assert [mock.call('Answer: ')] == interactive_secret_provider.input.call_args_list
