from unittest import TestCase
from sqlalchemy import create_engine, text
from config import database_config, queue_config, OracleQueueConfig, OracleDatabaseConfig
from database_queue import OracleQueue


class TestOracleQueue(TestCase):
    def setUp(self):
        assert isinstance(database_config, OracleDatabaseConfig)
        _config = {
            'name': f't_{queue_config.name}',
            'message_type': f't_{queue_config.message_type}',
            'service': f't_{queue_config.service}',
            'contract': f't_{queue_config.contract}'
        }
        self.config = OracleQueueConfig(**_config)
        self.db_engine = create_engine(database_config.uri)

        sql_create_message_type = text(
            f'CREATE TYPE {self.config.message_type} AS object ( payload  CLOB );'
        )
        sql_create_queue = text(
            f"""BEGIN
                    DBMS_AQADM.CREATE_QUEUE_TABLE(
                        queue_table =>'{self.config.name}_tb',
                        queue_payload_type  => '{self.config.message_type}'
                        );
                    DBMS_AQADM.CREATE_QUEUE(
                        queue_name => '{self.config.name}',
                        queue_table => '{self.config.name}_tb',
                        max_retries => 65535
                        );
                    DBMS_AQADM.START_QUEUE(
                        queue_name => '{self.config.name}'
                        );
                END;
"""
        )
        conn = self.db_engine.connect()
        trans = conn.begin()
        try:
            conn.execute(sql_create_message_type)
            conn.execute(sql_create_queue)
        except Exception as e:
            trans.rollback()
            raise e
        else:
            trans.commit()
        finally:
            conn.close()

    def tearDown(self):
        sql_drop_message_type = text(f"DROP TYPE {self.config.message_type}")
        sql_drop_queue = text(
            f"""BEGIN
                    DBMS_AQADM.STOP_QUEUE( queue_name => '{self.config.name}' );
                    DBMS_AQADM.DROP_QUEUE( queue_name => '{self.config.name}' );
                    DBMS_AQADM.DROP_QUEUE_TABLE ( queue_table => '{self.config.name}_tb' );
                END;
"""
        )
        conn = self.db_engine.connect()
        trans = conn.begin()
        try:
            conn.execute(sql_drop_queue)
            conn.execute(sql_drop_message_type)
        except Exception as e:
            trans.rollback()
            raise e
        else:
            trans.commit()
        finally:
            conn.close()

    def test_dequeue_message(self):
        queue = OracleQueue(
            engine=self.db_engine,
            config=self.config)
        queue.enqueue_message('queue message test from python 测试')
        message = queue.dequeue_message()
        self.assertEqual(message.payload, 'queue message test from python 测试')
