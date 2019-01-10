import hashlib
from api.wechat import WeChatAgent
from config import WeChatConfig
from cache import notice_cache as cache
from log import logger


class Notification:
    def __init__(self, message, payload):
        self._message = message
        self._payload = payload

    @property
    def message(self):
        return self._message

    @property
    def payload(self):
        return self._payload

    @property
    def identity(self):
        md5 = hashlib.md5()
        md5.update(f'{self.message}_{self.payload}'.encode('utf8'))
        return md5.hexdigest()


class Channel:
    __cache = cache

    def __init__(self, agent):
        self._agent = agent

    def send(self, notification):
        pass

    @property
    def agent(self):
        return self._agent

    @property
    def cache(self):
        return self.__cache


class WeChatChannel(Channel):
    def __init__(self, config: WeChatConfig):
        agent = WeChatAgent(config)
        super().__init__(agent)

    def send(self, notification: Notification):
        if self.cache.get('last_notification_identity') != notification.identity:
            self.cache.set(key='last_notification_identity', value=notification.identity, expire=30)
            try:
                if notification.payload:
                    self.agent.send_media_message(notification.payload)
                self.agent.send_text_message(notification.message)
            except Exception as e:
                logger.warning(f'发送通知失败 : {e}', exc_info=True)
