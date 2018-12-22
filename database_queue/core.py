class Queue:

    def __init__(self, **kwargs):
        self._name = kwargs.get('name')
        self._message_type = kwargs.get('message_type')
        self._engine = kwargs.get('engine')

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
        self._payload = payload

    @property
    def payload(self):
        return self._payload
