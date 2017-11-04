```
 _____                           _            
|_   _|_ _ _ __   __ _  ___ _ __(_)_ __   ___ 
  | |/ _` | '_ \ / _` |/ _ \ '__| | '_ \ / _ \
  | | (_| | | | | (_| |  __/ |  | | | | |  __/
  |_|\__,_|_| |_|\__, |\___|_|  |_|_| |_|\___|
                 |___/                        
```


[![Latest PyPI version](https://img.shields.io/pypi/v/tangerine.svg)](https://pypi.python.org/pypi/tangerine)
[![CircleCI](https://circleci.com/gh/kevinjqiu/tangerine.svg?style=svg)](https://circleci.com/gh/kevinjqiu/tangerine)

API and scraper for the Tangerine Bank (Canada).

Install
=======

    pip install tangerine

Usage
=====

Authentication
--------------

```python
from tangerine import InteractiveSecretProvider, TangerineClient

secret_provider = InteractiveSecretProvider()
client = TangerineClient(secret_provider)

with client.login():
    ...

```

Using `InteractiveSecretProvider` will prompt user for username/account #, security challenge questions and PIN number.

The call to `client.login()` will initiate the login process. After the login is successful, subsequent calls to the API will be authenticated.

If `client.login()` is used as a context manager (i.e., `with client.login():`), logout will be automatically initiated after the code block exits
or any exception is raised.

List accounts
-------------

With an active session, use `client.list_accounts()`:

```python
with client.login():
    accounts = client.list_accounts()
```

List transactions
-----------------

```python
with client.login():
    accounts = client.list_accounts()
    start_date = datetime.date(2017, 10, 1)
    end_date = datetime.date(2017, 11, 1)
    client.list_transactions([acct['number'] for acct in accounts], start_date, end_date)
```

Download statements
-------------------

```python
with client.login():
    accounts = client.list_accounts()
    start_date = datetime.date(2017, 10, 1)
    end_date = datetime.date(2017, 11, 1)
    client.download_ofx(account[0], start_date, end_date)
```


Licence
=======

MIT.


Authors
=======

tangerine was written by Kevin J. Qiu <kevin@idempotent.ca>
