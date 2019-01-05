import toml
from unittest import TestCase
from sqlalchemy import create_engine, text
from database_queue import MssqlQueue
from config import database_config

config = database_config['mssql']


class TestMssqlQueue(TestCase):
    def setUp(self):

        uri = 'mssql+pyodbc://{username}:{password}@{host}:{port}/{database_name}?driver=ODBC Driver 17 for SQL Server'.format(
            **config
        )
        self.db_engine = create_engine(uri)
        self.queue_name = f't_{config["queue_name"]}'
        self.service_name = f't_{config["service_name"]}'
        self.contract_name = f't_{config["contract_name"]}'
        self.message_type_name = f't_{config["message_type_name"]}'

        sql_create_message_type = text(
            f"CREATE MESSAGE TYPE [{self.message_type_name}] VALIDATION = NONE;"
        )
        sql_create_contract = text(
            f"CREATE CONTRACT [{self.contract_name}] ([{self.message_type_name}] SENT BY INITIATOR);"
        )
        sql_create_queue = text(
            f"CREATE QUEUE {self.queue_name} WITH STATUS = ON,RETENTION = OFF;"
        )
        sql_create_service = text(
            f"CREATE SERVICE [{self.service_name}] ON QUEUE {self.queue_name}([{self.contract_name}]);"
        )
        conn = self.db_engine.connect()
        trans = conn.begin()
        try:
            conn.execute(sql_create_message_type)
            conn.execute(sql_create_contract)
            conn.execute(sql_create_queue)
            conn.execute(sql_create_service)
        except Exception as e:
            trans.rollback()
            raise e
        else:
            trans.commit()
        finally:
            conn.close()

    def tearDown(self):
        sql_drop_message_type = text(
            f"IF EXISTS (SELECT * FROM sys.service_message_types WHERE name = N'{self.message_type_name}') DROP MESSAGE TYPE [{self.message_type_name}]"
        )
        sql_drop_contract = text(
            f"IF EXISTS (SELECT * FROM sys.service_contracts WHERE name = N'{self.contract_name}') DROP CONTRACT [{self.contract_name}]"
        )
        sql_drop_queue = text(
            f"IF EXISTS (SELECT * FROM sys.service_queues WHERE name = N'{self.queue_name}') DROP QUEUE [dbo].[{self.queue_name}]"
        )
        sql_drop_service = text(
            f"IF EXISTS (SELECT * FROM sys.services WHERE name = N'{self.service_name}') DROP SERVICE [{self.service_name}]"
        )
        conn = self.db_engine.connect()
        trans = conn.begin()
        try:
            conn.execute(sql_drop_service)
            conn.execute(sql_drop_queue)
            conn.execute(sql_drop_contract)
            conn.execute(sql_drop_message_type)
        except Exception as e:
            trans.rollback()
            raise e
        else:
            trans.commit()
        finally:
            conn.close()

    def test_dequeue_message(self):
        queue = MssqlQueue(
            engine=self.db_engine,
            **config)
        queue.enqueue_message('queue message test from python 测试')
        message = queue.dequeue_message()
        self.assertEqual(message.payload, 'queue message test from python 测试')
