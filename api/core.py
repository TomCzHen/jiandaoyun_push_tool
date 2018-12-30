import requests
from cache import api_cache as cache


class APIException(Exception):

    def __init__(self, code, message):
        self.code = code
        self.message = message


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
        except requests.exceptions.ConnectionError as e:
            raise e
        except requests.exceptions.Timeout as e:
            raise e
        except requests.exceptions.TooManyRedirects as e:
            raise e
        except APIException as e:
            raise e
        except requests.exceptions.HTTPError as e:
            raise e
        else:
            return response

    def _raise_api_error(self, response: requests.Response):
        pass
