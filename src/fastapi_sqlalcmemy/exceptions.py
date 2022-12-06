class FastAPISQLAlchemyError(Exception):
    """"""


class SQLAlchemyNotInitError(FastAPISQLAlchemyError):
    msg = """
    SQLAlchemy not init, please init first.
    eg:
    db = SQLAlchemy('sqlite+aiosqlite:////')
    db.init()
    """

    def __init__(self):
        super().__init__()
