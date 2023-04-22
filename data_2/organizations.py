import sqlalchemy
from data_2.db_session1 import SqlAlchemyBase


# база данных с запросами для разных типов организаций
class Organizations(SqlAlchemyBase):
    __tablename__ = 'organizations'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    request_about = sqlalchemy.Column(sqlalchemy.String, nullable=True)