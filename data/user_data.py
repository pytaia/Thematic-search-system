import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


# база данных с пользователями
class UserData(SqlAlchemyBase):
    __tablename__ = 'user_data'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    login = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    address = sqlalchemy.Column(sqlalchemy.String)
    # предлагаю здесь хранить последние три адреса, разделенные каким-то символом

    questions = orm.relationship("RequestHistory", back_populates='user')