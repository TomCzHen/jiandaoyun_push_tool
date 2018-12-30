class InvalidPayload(Exception):
    pass


class PayloadDecodeError(InvalidPayload, TypeError):
    pass


class PayloadKeyError(InvalidPayload, KeyError):
    pass
