import json
import os
from unittest import TestCase
from handlers import ContactsHandler
from sqlalchemy import create_engine
from config import database_config, sync_config, SyncConfig


class TestSyncHandler(TestCase):
    def setUp(self):
        self._db_engine = create_engine(database_config.uri)

        _config = {
            "users_table": f"t_{sync_config.users_table}",
            "departments_table": f"t_{sync_config.departments_table}",
            "relationships_table": f"t_{sync_config.relationships_table}",
        }
        test_sync_config = SyncConfig(**_config)
        self.handler = ContactsHandler(engine=self._db_engine, config=test_sync_config)

    def tearDown(self):
        self.handler.relationships_table.drop(self._db_engine, checkfirst=True)
        self.handler.users_table.drop(self._db_engine, checkfirst=True)
        self.handler.departments_table.drop(self._db_engine, checkfirst=True)

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

        users_data = json.loads(raw_users_json)['users']
        departments_data = json.loads(raw_departments_json)['departments']

        self.handler.handle(users=users_data, departments=departments_data)

        users_list = [(user['_id'], user['name']) for user in users_data]
        departments_list = [
            (department['_id'], department['parent_id'], department['name']) for department in departments_data
        ]

        with self._db_engine.connect() as conn:
            query_users = conn.execute(self.handler.users_table.select(), autocommit=True).fetchall()
            query_departments = conn.execute(self.handler.departments_table.select(), autocommit=True).fetchall()

        self.assertListEqual(query_users, users_list)
        self.assertListEqual(query_departments, departments_list)
