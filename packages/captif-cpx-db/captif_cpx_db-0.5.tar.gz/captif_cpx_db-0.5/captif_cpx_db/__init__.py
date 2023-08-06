__version__ = "0.5"

from sqlmodel import SQLModel
from captif_db_config import DbSession as BaseDbSession

from .constants import DEFAULT_DATABASE_NAME


class DbSession(BaseDbSession):
    database = DEFAULT_DATABASE_NAME
    metadata = SQLModel.metadata
