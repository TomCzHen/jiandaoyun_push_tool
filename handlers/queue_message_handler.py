import json
import hashlib
from formdata import FormData
from api import JianDaoYun
from handlers.exceptions import PayloadDecodeError, PayloadKeyError, SafeDataLimitException
from database_queue import QueueMessage
from cache import widgets_cache as cache


def generate_form_data_identity(payload: dict) -> str:
    identity_str = ''.join(payload['data'].keys())
    for value in payload['data'].values():
        if value and isinstance(value, list) and isinstance(value[0], dict):
            sub_identity_str = ''.join(value[0].keys())
            identity_str = ''.join([identity_str, sub_identity_str])

    identity_str = ''.join([identity_str, payload.get('etag', '')])
    md5 = hashlib.md5()
    md5.update(identity_str.encode('utf8'))
    return md5.hexdigest()


class Handler:
    def __init__(self, api: JianDaoYun):
        self._api = api

    def handle(self, message):
        form_data = self._init_form_data(message)
        self._handle_form_data(form_data)

    def _handle_form_data(self, form_data: FormData):
        handle_funcs = {
            'create': self._create_from_data,
            'update': self._update_from_data,
            'delete': self._delete_form_data
        }
        exists_data = self._query_exists_form_data(form_data)
        form_data.exists_data = exists_data
        handle_func = handle_funcs[form_data.operate.lower()]
        handle_func(form_data)

    def _create_from_data(self, form_data: FormData):

        if len(form_data.exists_data) > 1:
            self._delete_form_data(form_data)

        if len(form_data.exists_data) == 1:
            self._update_from_data(form_data)
        else:
            self._api.create_form_data(
                app_id=form_data.app_id,
                entry_id=form_data.entry_id,
                form_data=form_data.schema.data,
                is_start_workflow=form_data.is_start_workflow
            )

    def _update_from_data(self, form_data: FormData):

        if len(form_data.exists_data) == 1:
            self._api.update_form_data(
                app_id=form_data.app_id,
                entry_id=form_data.entry_id,
                form_data=form_data.schema.data,
                data_id=form_data.exists_data[0]
            )
        else:
            self._create_from_data(form_data)

    def _delete_form_data(self, form_data: FormData):
        for data_id in form_data.exists_data:
            self._api.delete_form_data(
                app_id=form_data.app_id,
                entry_id=form_data.entry_id,
                data_id=data_id['_id']
            )

    def _query_exists_form_data(self, form_data: FormData) -> list:
        response = self._api.query_form_data(form_data.app_id, form_data.entry_id, form_data.data_filter)
        form_data_list = response.json().get('data', [])
        limit = getattr(self._api, f'{form_data.operate.lower()}_safe_limit')
        if len(form_data_list) > limit:
            raise SafeDataLimitException
        return form_data_list

    def _init_form_data(self, message: QueueMessage) -> FormData:
        try:
            payload = json.loads(message.payload)
            widgets = self._get_from_data_widgets(payload)
            form_data = FormData(widgets=widgets, payload=payload)
        except json.decoder.JSONDecodeError as e:
            raise PayloadDecodeError(e.msg)
        except KeyError as e:
            raise PayloadKeyError(e)
        else:
            return form_data

    def _get_from_data_widgets(self, payload: dict) -> list:
        widgets: dict = cache.get(f'{payload["app_id"]}-{payload["entry_id"]}', None)
        identity = generate_form_data_identity(payload)
        if not widgets or widgets.get('identity', '') != identity:
            widgets = self._api.fetch_form_widgets(app_id=payload["app_id"], entry_id=payload["entry_id"])
            widgets['identity'] = identity
            cache.set(f'{payload["app_id"]}-{payload["entry_id"]}', widgets)
        return widgets['widgets']
