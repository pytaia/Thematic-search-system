import sqlalchemy
from .db_session1 import SqlAlchemyBase


class Parameters(SqlAlchemyBase):
    __tablename__ = 'parameters'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    address = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    coordinates = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    opening_hours = sqlalchemy.Column(sqlalchemy.String, nullable=True)