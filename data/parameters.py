import sqlalchemy
from .db_session1 import SqlAlchemyBase


class Parameters(SqlAlchemyBase):
    __tablename__ = 'parameters'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name_param = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    keys = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    # указать строки title, address, coordinates, opening_hours