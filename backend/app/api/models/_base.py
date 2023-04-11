import sqlalchemy.ext.declarative
from ...core import postgres


Base = sqlalchemy.ext.declarative.declarative_base(
    metadata=postgres.metadata,
)
