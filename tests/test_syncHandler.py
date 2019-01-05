import json
import os
from unittest import TestCase
from handlers import SyncHandler
from sqlalchemy import create_engine
from config import database_config, sync_config, db_driver


class TestSyncHandler(TestCase):
    def setUp(self):
        uri_formats = {
            'oracle': 'oracle+cx_oracle://{username}:{password}@{host}:{port}/{database_name}',
            'mssql': 'mssql+pyodbc://{username}:{password}@{host}:{port}/{database_name}?driver=ODBC Driver 17 for SQL Server'
        }

        _config: dict = database_config[db_driver]
        if db_driver.lower() == 'oracle':
            os.environ['NLS_LANG'] = _config.get('nls_lang')
            os.environ['LD_LIBRARY_PATH'] = _config.get('ld_library_path')

        uri = uri_formats[db_driver.lower()].format(**_config)
        self._db_engine = create_engine(uri)
        self.user_table_name = f"t_{sync_config['users_table']}"

    def test_handle(self):
        raw_users_json = """
{
    "users":[
        {
            "_id":"test_user_id-1",
            "name":"测试用户1",
            "username":"test_user_name-1",
            "departments":[
                "test_department-1"
            ]
        },
        {
            "_id":"test_user_id-2",
            "name":"测试用户2",
            "username":"test_user_name-2",
            "departments":[
                "test_department-1"
            ]
        },
        {
            "_id":"test_user_id-3",
            "name":"测试用户3",
            "username":"test_user_name-3",
            "departments":[
                "test_department-2"
            ]
        },
        {
            "_id":"test_user_id-4",
            "name":"测试用户4",
            "username":"test_user_name-4",
            "departments":[
                "test_department-2"
            ]
        },
        {
            "_id":"test_user_id-5",
            "name":"测试用户5",
            "username":"test_user_name-5",
            "departments":[
                "test_department-1",
                "test_department-2"
            ]
        },
        {
            "_id":"test_user_id-6",
            "name":"测试用户6",
            "username":"test_user_name-5",
            "departments":[
                "test_department-3"
            ]
        }
    ]
}
        """
        raw_departments_json = """
{
    "departments":[
        {
            "_id":"test_department-0",
            "name":"测试部门",
            "parent_id":"root"
        },
        {
            "_id":"test_department-1",
            "name":"测试部门1",
            "parent_id":"test_department-0"
        },
        {
            "_id":"test_department-2",
            "name":"测试部门2",
            "parent_id":"test_department-1"
        },
        {
            "_id":"test_department-3",
            "name":"测试部门3",
            "parent_id":"test_department-2"
        }
    ]
}
        """
        users = json.loads(raw_users_json)['users']
        departments = json.loads(raw_departments_json)['departments']
        sync_handler = SyncHandler(engine=self._db_engine, **sync_config)
        sync_handler.handle(users=users, departments=departments)
