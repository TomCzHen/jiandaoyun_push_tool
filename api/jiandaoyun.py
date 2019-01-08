from requests import Response
from requests.exceptions import HTTPError
from ratelimiter import RateLimiter
from .core import API, APIException
from config import JdyApiConfig


class BadRequestParamsException(APIException):
    def __init__(self, **kwargs):
        super().__init__(code='3005', message=kwargs.get('message'))


class DataSubmitFailException(APIException):
    def __init__(self, **kwargs):
        super().__init__(code='4000', message=kwargs.get('message'))


class DataNotExistException(APIException):
    def __init__(self, **kwargs):
        super().__init__(code='4001', message=kwargs.get('message'))


class InvalidSignatureException(APIException):
    def __init__(self, **kwargs):
        super().__init__(code='8301', message=kwargs.get('message'))


class UnauthorizedException(APIException):
    def __init__(self, **kwargs):
        super().__init__(code='8302', message=kwargs.get('message'))


class TooManyRequestException(APIException):
    def __init__(self, **kwargs):
        super().__init__(code='8303', message=kwargs.get('message'))


class DepartmentNotExistException(APIException):
    def __init__(self, **kwargs):
        super().__init__(code='6002', message=kwargs.get('message'))


class UserNotExistException(APIException):
    def __init__(self, **kwargs):
        super().__init__(code='1010', message=kwargs.get('message'))


class UnknownAPIException(APIException):
    def __init__(self, **kwargs):
        super().__init__(code=kwargs.get('code'), message=kwargs.get('message'))


API_EXCEPTIONS = {
    3005: BadRequestParamsException,
    4000: DataSubmitFailException,
    4001: DataNotExistException,
    8301: InvalidSignatureException,
    8302: UnauthorizedException,
    8303: TooManyRequestException,
    6002: DepartmentNotExistException,
    1010: UserNotExistException,
}


class JianDaoYun(API):
    def __init__(self, config: JdyApiConfig):
        self._api_key = config.api_key
        self._safe_limit: dict = config.safe_limit
        super().__init__(scheme='https', host='www.jiandaoyun.com', base_path='api/v1')

    @property
    def api_key(self):
        return self._api_key

    @property
    def create_safe_limit(self):
        limit = self._safe_limit.get('create', 0)
        if limit > 10:
            limit = 10
        if limit < 0:
            limit = 0
        return limit

    @property
    def update_safe_limit(self):
        limit = self._safe_limit.get('update', 1)
        if limit > 10:
            limit = 10
        if limit < 1:
            limit = 1
        return limit

    @property
    def delete_safe_limit(self):
        limit = self._safe_limit.get('delete', 0)
        if limit > 10:
            limit = 10
        if limit < 1:
            limit = 1
        return limit

    def fetch_form_widgets(self, app_id: str, entry_id: str) -> Response:
        assert app_id != ''
        assert entry_id != ''
        """
        POST - /api/v1/app/{app_id}/entry/{entry_id}/widgets 
        表单字段查询接口
        获取指定表单除分割线控件和关联查询控件以外的控件/字段信息。
        """
        method = 'POST'
        path = f'app/{app_id}/entry/{entry_id}/widgets'
        response = self._request(method=method, path=path)

        return response

    def query_form_data(self, app_id: str, entry_id: str, data_filter: dict = None):
        assert app_id != ''
        assert entry_id != ''
        assert data_filter != {}
        """
        POST - /api/v1/app/{app_id}/entry/{entry_id}/data
        查询多条数据接口
        该接口的返回数据，始终按照数据ID正序排列。
        """
        method = 'POST'
        path = f'app/{app_id}/entry/{entry_id}/data'
        data = {
            "data_id": "",
            **data_filter
        }

        response = self._request(method=method, path=path, data=data)
        return response

    def fetch_form_data(self, app_id: str, entry_id: str, data_id: str):
        assert app_id != ''
        assert entry_id != ''
        assert data_id != ''
        """
        POST - /api/v1/app/{app_id}/entry/{entry_id}/data_retrieve
        查询单条数据接口
        按照指定数据ID获取表单中的数据。
        """
        method = 'POST'
        path = f'app/{app_id}/entry/{entry_id}/data_retrieve'
        data = {
            "data_id": data_id,
        }
        response = self._request(method=method, path=path, data=data)
        return response

    def create_form_data(self, app_id: str, entry_id: str, form_data: dict = None, is_start_workflow: bool = False):
        """
        POST - /api/v1/app/{app_id}/entry/{entry_id}/data_create
        新建单条数据接口
        在指定表单中添加一条数据。
        """
        assert app_id != ''
        assert entry_id != ''
        assert form_data != {}
        data = {
            "data": form_data,
            "is_start_workflow": is_start_workflow
        }
        method = 'POST'
        path = f'app/{app_id}/entry/{entry_id}/data_create'
        response = self._request(method=method, path=path, data=data)

        return response

    def update_form_data(self, app_id: str, entry_id: str, data_id: str, form_data: dict = None):
        """
        POST - /api/v1/app/{app_id}/entry/{entry_id}/data_update
        修改单条数据接口
        按照指定数据ID修改表单中的数据。
        """
        assert app_id != ''
        assert entry_id != ''
        assert form_data != {}
        assert data_id != ''
        data = {
            "data_id": data_id,
            "data": form_data
        }
        method = 'POST'
        path = f'app/{app_id}/entry/{entry_id}/data_update'
        response = self._request(method=method, path=path, data=data)

        return response

    def delete_form_data(self, app_id: str, entry_id: str, data_id: str):
        """
        POST - /api/v1/app/{app_id}/entry/{entry_id}/data_delete
        删除单条数据接口
        按照指定数据ID从表单中删除数据。
        """
        assert app_id != ''
        assert entry_id != ''
        assert data_id != ''
        data = {
            "data_id": data_id,
        }
        method = 'POST'
        path = f'app/{app_id}/entry/{entry_id}/data_delete'
        response = self._request(method=method, path=path, data=data)

        return response

    def fetch_department_list(self, dept_id: str = 'root', has_child: bool = False):
        """
        POST /api/v1/department/{ dept_id }/department_list
        （递归）获取指定部门的子部门列表
        能够（递归）获取指定部门id的所有子部门。
        """
        assert dept_id != ''
        data = {
            "has_child": has_child
        }
        method = 'POST'
        path = f'department/{dept_id}/department_list'
        response = self._request(method=method, path=path, data=data)
        return response

    def fetch_member_list(self, dept_id: str = 'root', has_child: bool = False):
        """
        POST /api/v1/department/{dept_id}/member_list
        （递归）获取指定部门里的成员列表
        """
        assert dept_id != ''
        data = {
            "has_child": has_child
        }
        method = 'POST'
        path = f'department/{dept_id}/member_list'
        response = self._request(method=method, path=path, data=data)
        return response

    def fetch_user(self, user_id: str):
        """
        POST /api/v1/user/{user_id}/user_retrieve 获取指定成员信息
        """
        assert user_id != ''
        method = 'POST'
        path = f'user/{user_id}/user_retrieve'
        response = self._request(method=method, path=path)
        return response

    def _raise_api_error(self, response: Response):
        try:
            response.raise_for_status()
        except HTTPError as error:
            if response.status_code == 400:
                response_dict = response.json()
                code = response_dict.get('code')
                message = response_dict.get('msg', '')
                exception = API_EXCEPTIONS.get(code, UnknownAPIException)(code=code, message=message)
                raise exception
            else:
                raise error

    @RateLimiter(max_calls=5, period=1)
    def _request(self, method: str = 'GET', headers: dict = None, path: str = '', params=None, data: dict = None,
                 files=None, timeout=10):

        response = super()._request(
            method=method,
            headers=headers,
            path=path,
            params=params,
            data=data,
            files=files,
            timeout=timeout
        )
        return response
