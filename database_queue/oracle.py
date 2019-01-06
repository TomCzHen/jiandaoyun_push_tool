from .core import Queue, QueueMessage
from cx_Oracle import Connection, DEQ_FIRST_MSG, DEQ_NO_WAIT, DatabaseError


class OracleQueueMessage(QueueMessage):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def create_message(cls, message):
        payload = str(message.PAYLOAD)
        return cls(payload=payload)


class OracleQueue(Queue):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def dequeue_message(self):
        conn: Connection = self.engine.raw_connection()
        message_options = conn.deqoptions()
        message_properties = conn.msgproperties()
        message_type = conn.gettype(self.message_type)
        message_options.navigation = DEQ_FIRST_MSG
        message_options.wait = DEQ_NO_WAIT
        message = message_type.newobject()
        conn.begin()
        try:
            if conn.deq(self.name, message_options, message_properties, message):
                queue_message = OracleQueueMessage.create_message(message)
                conn.commit()
                conn.close()
                return queue_message
        except DatabaseError as e:
            conn.rollback()
            conn.close()
            raise e

    def enqueue_message(self, payload: str):
        conn: Connection = self._engine.raw_connection()
        message_options = conn.enqoptions()
        message_properties = conn.msgproperties()
        message_type = conn.gettype(self.message_type)
        message = message_type.newobject()
        message.PAYLOAD = payload.encode('utf-8')
        conn.begin()
        try:
            conn.enq(self.name, message_options, message_properties, message)
        except DatabaseError as e:
            conn.rollback()
            conn.close()
            raise e
        else:
            conn.commit()
