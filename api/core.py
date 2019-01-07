import requests
from log import logger
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects


class APIException(Exception):

    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return self.message


class NetworkError(IOError):
    pass


class API:

    def __init__(self, host: str, base_path: str, scheme: str = 'http'):
        assert scheme.lower() in ['http', 'https']
        assert host != ''
        assert base_path != ''
        self._scheme = scheme
        self._host = host
        self._base_path = base_path

    @property
    def host(self):
        return self._host

    @property
    def base_path(self):
        return self._base_path

    @property
    def scheme(self):
        return self._scheme

    @property
    def base_url(self):
        return f'{self.scheme}://{self.host}/{self.base_path}'

    def _request(self, method: str = 'GET', headers: dict = None, path: str = '', params=None, data: dict = None,
                 files=None, timeout=10) -> requests.Response:
        url = f'{self.base_url}/{path}'
        headers = dict() if headers is None else headers

        try:
            response = requests.request(
                method=method,
                headers=headers,
                url=url,
                params=params,
                json=data,
                files=files,
                timeout=timeout
            )
            self._raise_api_error(response)
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            logger.error(e, exc_info=True)
            raise NetworkError
        else:
            return response

    def _raise_api_error(self, response: requests.Response):
        pass
