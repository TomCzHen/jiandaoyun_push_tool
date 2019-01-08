from unittest import TestCase
from sqlalchemy import create_engine, text
from database_queue import MssqlQueue
from config import database_config, queue_config, MssqlQueueConfig, MssqlDatabaseConfig


class TestMssqlQueue(TestCase):
    def setUp(self):
        assert isinstance(database_config, MssqlDatabaseConfig)
        _config = {
            'name': f't_{queue_config.name}',
            'message_type': f't_{queue_config.message_type}',
            'service': f't_{queue_config.service}',
            'contract': f't_{queue_config.contract}'
        }
        self.config = MssqlQueueConfig(**_config)
        self.db_engine = create_engine(database_config.uri)

        sql_create_message_type = text(
            f"CREATE MESSAGE TYPE [{self.config.message_type}] VALIDATION = NONE;"
        )
        sql_create_contract = text(
            f"CREATE CONTRACT [{self.config.contract}] ([{self.config.message_type}] SENT BY INITIATOR);"
        )
        sql_create_queue = text(
            f"CREATE QUEUE {self.config.name} WITH STATUS = ON,RETENTION = OFF,POISON_MESSAGE_HANDLING (STATUS = OFF);"
        )
        sql_create_service = text(
            f"CREATE SERVICE [{self.config.service}] ON QUEUE {self.config.name}([{self.config.contract}]);"
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
            f"IF EXISTS (SELECT * FROM sys.service_message_types WHERE name = N'{self.config.message_type}') DROP MESSAGE TYPE [{self.config.message_type}]"
        )
        sql_drop_contract = text(
            f"IF EXISTS (SELECT * FROM sys.service_contracts WHERE name = N'{self.config.contract}') DROP CONTRACT [{self.config.contract}]"
        )
        sql_drop_queue = text(
            f"IF EXISTS (SELECT * FROM sys.service_queues WHERE name = N'{self.config.name}') DROP QUEUE [dbo].[{self.config.name}]"
        )
        sql_drop_service = text(
            f"IF EXISTS (SELECT * FROM sys.services WHERE name = N'{self.config.service}') DROP SERVICE [{self.config.service}]"
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
            config=self.config)
        queue.enqueue_message('queue message test from python 测试')
        message = queue.dequeue_message()
        self.assertEqual(message.payload, 'queue message test from python 测试')
