from __future__ import annotations

from sqlalchemy.dialects.postgresql import ARRAY, REAL
from sqlalchemy.types import UserDefinedType


class Embedding(UserDefinedType):
    cache_ok = True

    def __init__(self, dimensions: int) -> None:
        self.dimensions = dimensions

    def get_col_spec(self) -> str:
        return f"embedding({self.dimensions})"

    def bind_processor(self, dialect):
        return ARRAY(REAL).bind_processor(dialect)

    def result_processor(self, dialect, coltype):
        return ARRAY(REAL).result_processor(dialect, coltype)
