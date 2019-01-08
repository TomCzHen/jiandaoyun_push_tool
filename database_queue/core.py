from config import QueueConfig


class Queue:

    def __init__(self, engine, config: QueueConfig):
        self._engine = engine
        self._name = config.name
        self._message_type = config.message_type

    @property
    def name(self):
        return self._name

    @property
    def message_type(self):
        return self._message_type

    @property
    def engine(self):
        return self._engine

    def dequeue_message(self):
        pass

    def enqueue_message(self, payload: str):
        pass


class QueueMessage:
    def __init__(self, payload):
        self._payload: str = payload

    @property
    def payload(self):
        return self._payload

    def __str__(self):
        return self._payload


class QueueException(Exception):
    pass
