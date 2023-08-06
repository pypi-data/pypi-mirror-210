import tempfile
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy.engine import Engine

from turandot.meta import Singleton
from turandot.model import ModelUtils, ConfigModel
from turandot.model.sql import Base


class DbEngine(metaclass=Singleton):
    """Engine to connect ORM to a database"""

    @staticmethod
    def _get_production_path() -> Path:
        return ModelUtils.get_config_dir() / "assets.db"

    @staticmethod
    def _get_test_path() -> Path:
        return Path(tempfile.gettempdir()) / "turandot_assets.db"

    @staticmethod
    def _delete_test_db():
        DbEngine._get_test_path().unlink(missing_ok=True)

    def __init__(self):
        if ConfigModel().get_key(['debug', 'use_tmp_db']):
            DbEngine._delete_test_db()
            dbpath = f"sqlite:///{DbEngine._get_test_path()}"
        else:
            dbpath = f"sqlite:///{DbEngine._get_production_path()}"
        self.engine = create_engine(dbpath, future=True)
        Base.metadata.create_all(self.engine, checkfirst=True)

    def use_test_db(self, echo=False) -> None:
        DbEngine._delete_test_db()
        dbpath = f"sqlite:///{DbEngine._get_test_path()}"
        self.engine = create_engine(dbpath, future=True, echo=echo)
        Base.metadata.create_all(self.engine)

    def create_session(self):
        session_factory = sessionmaker(bind=self.engine)
        return session_factory()
