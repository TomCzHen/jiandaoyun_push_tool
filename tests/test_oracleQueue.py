import toml
from unittest import TestCase
from sqlalchemy import create_engine, text, func


class TestOracleQueue(TestCase):
    def setUp(self):
        config = toml.load('../config.toml')['database']['oracle']
        uri = 'oracle+cx_oracle://{username}:{password}@{host}:{port}/{database_name}'.format(**config)
        self.db_engine = create_engine(uri)
        self.queue_name = f't_{config["queue_name"]}'
        self.message_type_name = f't_{config["message_type_name"]}'

        sql_create_message_type = text(
            f'CREATE TYPE {self.message_type_name} AS object ( payload  CLOB );'
        )
        sql_create_queue = text(
            f"""BEGIN
                    DBMS_AQADM.CREATE_QUEUE_TABLE(
                        queue_table =>'{self.queue_name}tb',
                        queue_payload_type  => '{self.message_type_name}'
                        );
                    DBMS_AQADM.CREATE_QUEUE(
                        queue_name => '{self.queue_name}',
                        queue_table => '{self.queue_name}tb',
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
            # raise e
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
                    DBMS_AQADM.DROP_QUEUE_TABLE ( queue_table => '{self.queue_name}tb' );
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
        self.fail()
