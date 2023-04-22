import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


# база данных со списком запросов пользователей к системе
class RequestHistory(SqlAlchemyBase):
    __tablename__ = 'request_history'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("user_data.id"))
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    question = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    answer = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    user = orm.relationship('UserData')