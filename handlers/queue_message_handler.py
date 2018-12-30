import json
import hashlib
from formdata import FormData
from api import JianDaoYun
from database_queue import QueueMessage
from handlers.exceptions import PayloadDecodeError, PayloadKeyError

from cache import widgets_cache as cache


class Handler:
    def __init__(self, api: JianDaoYun):
        self._api = api

    def create_form_data(self, message: QueueMessage):
        try:
            payload = json.loads(message.payload)
            widgets = self._get_from_data_widgets(payload)
            form_data = FormData.create_form_data(widgets=widgets, payload=payload)
        except json.decoder.JSONDecodeError:
            raise PayloadDecodeError
        except KeyError:
            raise PayloadKeyError
        else:
            return form_data

    def _get_from_data_widgets(self, payload: dict) -> list:
        widgets: dict = cache.get(f'{payload["app_id"]}-{payload["entry_id"]}', None)
        identity = self.generate_form_data_identity(payload)
        if not widgets or widgets.get('identity', '') != identity:
            widgets = self._api.fetch_form_widgets(app_id=payload["app_id"], entry_id=payload["entry_id"])
            widgets['identity'] = identity
            cache.set(f'{payload["app_id"]}-{payload["entry_id"]}', widgets)
        return widgets['widgets']

    @staticmethod
    def generate_form_data_identity(payload: dict) -> str:
        identity_str = ''.join(payload['data'].keys())
        for value in payload.values():
            if value and isinstance(value, list) and isinstance(value[0], dict):
                sub_identity_str = ''.join(value[0].keys())
                identity_str = ''.join([identity_str, sub_identity_str])

        identity_str = ''.join([identity_str, payload.get('etag', '')])
        md5 = hashlib.md5()
        md5.update(identity_str.encode('utf8'))
        return md5.hexdigest()
