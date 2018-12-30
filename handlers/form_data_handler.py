from api import JianDaoYun
from formdata import FormData


class Handler:
    def __init__(self, api: JianDaoYun):
        self._api = api

    def handle_form_data(self, form_data: FormData):
        pass
