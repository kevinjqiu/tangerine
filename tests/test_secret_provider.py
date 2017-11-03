import mock
from pytest import fixture
from tangerine import InteractiveSecretProvider, DictionaryBasedSecretProvider


@fixture
def interactive_secret_provider():
    return InteractiveSecretProvider(input=mock.Mock(), getpass=mock.Mock())


@fixture
def dict_secret_provider():
    return DictionaryBasedSecretProvider({
        'username': 'USERNAME',
        'password': 'PASSWORD',
        'security_questions': {'Q1': 'A1', 'Q2': 'A2'},
    })


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


def test_dict_secret_provider___get_username(dict_secret_provider):
    assert 'USERNAME' == dict_secret_provider.get_username()


def test_dict_secret_provider___get_password(dict_secret_provider):
    assert 'PASSWORD' == dict_secret_provider.get_password('')


def test_dict_secret_provider___get_security_challenge_answer(dict_secret_provider):
    assert 'A1' == dict_secret_provider.get_security_challenge_answer('Q1')


def test_dict_secret_provider___get_security_challenge_answer___no_answer(dict_secret_provider):
    assert None is dict_secret_provider.get_security_challenge_answer('Q3')
