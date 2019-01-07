class InvalidPayload(Exception):
    def __init__(self, msg):
        self.msg = f'{msg}'
        super().__init__(self.msg)

    def __str__(self):
        return self.msg


class PayloadDecodeError(InvalidPayload):
    def __init__(self, msg):
        self.msg = f'JSON 解码错误 {msg}'
        super().__init__(self.msg)


class PayloadKeyError(InvalidPayload, KeyError):
    def __init__(self, msg):
        self.msg = f'缺少必须键 ： {msg}'
        super().__init__(self.msg)


class HandlerException(Exception):
    def __init__(self, msg):
        self.msg = f'{msg}'
        super().__init__(self.msg)

    def __str__(self):
        return self.msg


class SafeDataLimitException(HandlerException):
    def __init__(self):
        self.msg = f'表单已存在数据超出安全限制。'
        super().__init__(self.msg)
