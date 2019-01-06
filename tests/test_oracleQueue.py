import os
from unittest import TestCase
from sqlalchemy import create_engine, text
from config import database_config, queue_config
from database_queue import OracleQueue


class TestOracleQueue(TestCase):
    def setUp(self):
        _db_config = database_config['oracle']
        _queue_config = queue_config['oracle']
        uri = 'oracle+cx_oracle://{username}:{password}@{host}:{port}/{database_name}'.format(**_db_config)
        os.environ['NLS_LANG'] = _db_config.get('nls_lang')
        os.environ['LD_LIBRARY_PATH'] = _db_config.get('ld_library_path')
        self.db_engine = create_engine(uri)
        self.queue_name = f't_{_queue_config["name"]}'
        self.message_type_name = f't_{_queue_config["message_type"]}'

        sql_create_message_type = text(
            f'CREATE TYPE {self.message_type_name} AS object ( payload  CLOB );'
        )
        sql_create_queue = text(
            f"""BEGIN
                    DBMS_AQADM.CREATE_QUEUE_TABLE(
                        queue_table =>'{self.queue_name}_tb',
                        queue_payload_type  => '{self.message_type_name}'
                        );
                    DBMS_AQADM.CREATE_QUEUE(
                        queue_name => '{self.queue_name}',
                        queue_table => '{self.queue_name}_tb',
                        max_retries => 65535
                        );
                    DBMS_AQADM.START_QUEUE(
                        queue_name => '{self.queue_name}'
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
        sql_drop_message_type = text(f"DROP TYPE {self.message_type_name}")
        sql_drop_queue = text(
            f"""BEGIN
                    DBMS_AQADM.STOP_QUEUE( queue_name => '{self.queue_name}' );
                    DBMS_AQADM.DROP_QUEUE( queue_name => '{self.queue_name}' );
                    DBMS_AQADM.DROP_QUEUE_TABLE ( queue_table => '{self.queue_name}_tb' );
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
        _config = {
            "name": self.queue_name,
            "message_type": self.message_type_name
        }
        queue = OracleQueue(
            engine=self.db_engine,
            **_config)
        queue.enqueue_message('queue message test from python 测试')
        message = queue.dequeue_message()
        self.assertEqual(message.payload, 'queue message test from python 测试')
