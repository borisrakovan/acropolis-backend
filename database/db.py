import json
from decimal import Decimal
from enum import Enum
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlmodel import SQLModel

db_file = Path.cwd() / "app.db"

SQLALCHEMY_DATABASE_URL = "sqlite:///" + str(db_file)


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        # 👇️ if passed in object is instance of Decimal
        # convert it to a string
        if isinstance(obj, Decimal):
            return str(obj)

        from database.models.monitoring_rules import AreaDefinition, TimeWindowDefinition
        if isinstance(obj, AreaDefinition):
            return obj.__root__.dict()
        if isinstance(obj, TimeWindowDefinition):
            return obj.dict()
        if isinstance(obj, Enum):
            return obj.value

        # 👇️ otherwise use the default behavior
        return json.JSONEncoder.default(self, obj)


def dumps(obj):
    return json.dumps(obj, cls=DecimalEncoder)


engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, echo=True,
    json_serializer=dumps
)


def create_db_and_tables():
    from database.models.alerts import AlertDefinition
    from database.models.monitoring_rules import MonitoringRule

    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    create_db_and_tables()
