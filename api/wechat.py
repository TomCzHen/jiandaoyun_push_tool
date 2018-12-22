from .core import API, APIException, cache


class SystemBusyException(APIException):
    def __init__(self, **kwargs):
        super().__init__(code=-1, message=kwargs.get('message'))


class InvalidSecretException(APIException):
    def __init__(self, **kwargs):
        super().__init__(code=40001, message=kwargs.get('message'))


class InvalidCorpIDException(APIException):
    def __init__(self, **kwargs):
        super().__init__(code=40013, message=kwargs.get('message'))


class InvalidAgentIDException(APIException):
    def __init__(self, **kwargs):
        super().__init__(code=40056, message=kwargs.get('message'))


class InvalidAccessTokenException(APIException):
    def __init__(self, **kwargs):
        super().__init__(code=40014, message=kwargs.get('message'))


class InvalidUserIDException(APIException):
    def __init__(self, **kwargs):
        super().__init__(code=40003, message=kwargs.get('message'))


class UserIDNotExistException(APIException):
    def __init__(self, **kwargs):
        super().__init__(code=40031, message=kwargs.get('message'))


class PartyIDNotExistException(APIException):
    def __init__(self, **kwargs):
        super().__init__(code=40031, message=kwargs.get('message'))


class InvalidMediaFileException(APIException):
    def __init__(self, **kwargs):
        super().__init__(code=40004, message=kwargs.get('message'))


class InvalidMediaTypeException(APIException):
    def __init__(self, **kwargs):
        super().__init__(code=40005, message=kwargs.get('message'))


class InvalidMediaSizeException(APIException):
    def __init__(self, **kwargs):
        super().__init__(code=40006, message=kwargs.get('message'))


class InvalidMediaIDException(APIException):
    def __init__(self, **kwargs):
        super().__init__(code=40007, message=kwargs.get('message'))


class InvalidMessageTypeException(APIException):
    def __init__(self, **kwargs):
        super().__init__(code=40008, message=kwargs.get('message'))


class TooManyRequestException(APIException):
    def __init__(self, **kwargs):
        super().__init__(code=45009, message=kwargs.get('message'))


class WeChat(API):

    def __init__(self, corp_id):
        self._corp_id = corp_id
        super().__init__(scheme='https', host='qyapi.weixin.qq.com', base_path='cgi-bin')

    @property
    def corp_id(self):
        return self._corp_id

    @classmethod
    def create_agent(cls, corp_id, agent_id, agent_secret):
        api = cls(corp_id)
        agent = WeChatAgent(agent_id, agent_secret, api)
        return agent

    def get_access_token(self, secret):
        method = 'GET'
        params = {"corpid": self.corp_id, "corpsecret": secret}
        path = '/gettoken'
        response = self._request(method=method, path=path, params=params)
        return response

    def upload_media(self, access_token, payload, file_name, media_type='file'):
        method = 'POST'
        params = {'access_token': access_token, 'type': media_type}
        path = '/media/upload'
        media_file = {'file': (file_name, payload)}
        response = self._request(method=method, path=path, params=params, files=media_file)
        return response

    def send_media_message(self, access_token, media_id, party_id, agent_id):
        method = 'POST'
        params = {'access_token': access_token}
        path = '/message/send'
        data = {
            "toparty": party_id,
            "msgtype": "file",
            "agentid": agent_id,
            "file": {
                "media_id": media_id
            },
            "safe": 0
        }
        response = self._request(method=method, path=path, data=data, params=params)
        return response

    def send_text_message(self, access_token, payload: str, party_id, agent_id):
        method = 'POST'
        params = {'access_token': access_token}
        path = '/message/send'
        data = {
            "toparty": party_id,
            "msgtype": "text",
            "agentid": agent_id,
            "text": {
                "content": f"{payload}"
            }
        }
        response = self._request(method=method, path=path, data=data, params=params)
        return response


class WeChatAgent:
    def __init__(self, agent_id, agent_secret, api: WeChat):
        self._api = api
        self._id = agent_id
        self._secret = agent_secret

    @property
    def id(self):
        return self._id

    @property
    def secret(self):
        return self._secret

    @property
    def api(self):
        return self._api

    @property
    def access_token(self):
        key = f'{self.api.corp_id}-{self.id}-token'
        token = cache.get(key)
        if not token:
            response = self.api.get_access_token(self.secret)
            token = response.json().get('access_token')
            expire = response.json().get('expires_in') - 30
            cache.set(key=key, value=token, expire=expire)
        return token
