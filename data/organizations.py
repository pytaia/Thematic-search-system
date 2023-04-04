import sqlalchemy
from .db_session1 import SqlAlchemyBase


class Organizations(SqlAlchemyBase):
    __tablename__ = 'organizations'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    request_about = sqlalchemy.Column(sqlalchemy.String, nullable=True)