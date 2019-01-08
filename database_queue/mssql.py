from sqlalchemy.sql import text
from sqlalchemy.exc import ProgrammingError
from .core import Queue, QueueMessage, QueueException
from log import logger
from config import MssqlQueueConfig


class MssqlQueueMessage(QueueMessage):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def create_message(cls, message):
        payload = message['payload']
        return cls(payload=payload)


class MssqlQueue(Queue):
    def __init__(self, engine, config: MssqlQueueConfig):
        self._service = config.service
        self._contract = config.contract
        super().__init__(engine=engine, config=config)

    @property
    def service(self):
        return self._service

    @property
    def contract(self):
        return self._contract

    def dequeue_message(self):
        sql = text(
            f"WAITFOR ( RECEIVE TOP(1) CONVERT(nvarchar(max),message_body) AS 'payload' FROM {self.name}), TIMEOUT 0;"
        )
        conn = self.engine.connect()
        trans = conn.begin()
        try:
            message = conn.execute(sql).fetchone()
            if message:
                queue_message = MssqlQueueMessage.create_message(message)
                trans.commit()
                conn.close()
                return queue_message
            else:
                trans.commit()
                conn.close()
        except Exception as e:
            trans.rollback()
            conn.close()
            logger.error(e, exc_info=True)
            raise QueueException

    def enqueue_message(self, payload: str):
        sql = text(
            f"""DECLARE @DlgHandle UNIQUEIDENTIFIER;
                DECLARE @Message NVARCHAR(max);
                SELECT  @Message = N'{payload}';
                BEGIN DIALOG @DlgHandle
                FROM SERVICE [{self.service}]
                TO SERVICE N'{self.service}', 'CURRENT DATABASE'
                ON CONTRACT [{self.contract}]
                    WITH ENCRYPTION = OFF;
                SEND ON CONVERSATION  @DlgHandle MESSAGE TYPE [{self.message_type}]  ( @Message );"""
        )
        conn = self.engine.connect()
        trans = conn.begin()
        try:
            conn.execute(sql)
        except Exception as e:
            trans.rollback()
            conn.close()
            logger.error(e, exc_info=True)
            raise QueueException
        else:
            trans.commit()
