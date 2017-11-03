class APIResponseError(RuntimeError):
    def __init__(self, api_response):
        self.api_response = api_response

    def __str__(self):
        return 'The API request did not receive a successful response: {!r}'.format(self.api_response)


class UnsupportedAccountTypeForDownload(RuntimeError):
    def __init__(self, account_type):
        self.account_type = account_type

    def __str__(self):
        return 'Transaction download is not supported for account type {!r}'.format(self.account_type)
