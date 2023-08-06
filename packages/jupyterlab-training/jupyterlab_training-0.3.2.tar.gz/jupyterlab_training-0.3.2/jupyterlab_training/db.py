from datetime import datetime
import os
import shutil

import arrow
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy import (
    Column,
    JSON,
    Text,
)
from sqlalchemy_utils.types import ArrowType
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Student(Base):
    __tablename__ = "student"
    username = Column(Text, primary_key=True)
    done_exercises = Column(JSON)
    need_help_exercises = Column(JSON)
    up_date = Column(ArrowType, default=arrow.utcnow, onupdate=arrow.utcnow)


class Database:
    instance = None

    def __init__(self, url):
        Database.instance = self
        self.url = url
        try:
            # Set a timeout to make write operations more robust on SQLite
            self.connect_args = {
                "timeout": 10,
                "check_same_thread": False,
            }
            self._engine = self._create_engine()
            self.create_session = sessionmaker(bind=self._engine)
        except Exception as e:
            print(e)

    def _create_engine(self):
        return create_engine(self.url, connect_args=self.connect_args)

    def connect(self):
        return self._engine.connect()

    def create_all(self):
        print("initializing database {}".format(self.url))
        Base.metadata.create_all(self._engine)

    def drop_all(self):
        print("dropping database {}".format(self.url))
        Base.metadata.drop_all(self._engine)


def get_database_path():
    db_repo_path = os.path.expanduser("~/files/project_shared")
    if not os.path.exists(db_repo_path):
        db_repo_path = os.path.expanduser("~")
    db_path = os.path.join(db_repo_path, "logilab-training.db")
    return db_path


def create_db_session():
    db_path = get_database_path()
    database = Database("sqlite:///{}".format(db_path))
    if not os.path.exists(db_path):
        database.create_all()
        os.chmod(db_path, 0o666)
    return database.create_session()


def reset_db():
    db_path = get_database_path()
    date = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    shutil.copy(db_path, ".".join([db_path,  date]))
    database = Database("sqlite:///{}".format(db_path))
    database.drop_all()
    database.create_all()
