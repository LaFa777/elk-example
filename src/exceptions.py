class ViewException(Exception):
    """
    Базовый тип ошибки. Должен рейзиться из view для обработки на стороне middleware
    """

    def __init__(self, message: str, code: int):
        self.message = message
        self.code = code
