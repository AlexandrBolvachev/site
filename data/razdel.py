# Класс с описанием таблицы разделов

import datetime
import sqlalchemy
from sqlalchemy import orm

from db_session import SqlAlchemyBase


class Razdel(SqlAlchemyBase):
    __tablename__ = 'razdel'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    status = sqlalchemy.Column(sqlalchemy.String, default='True')

    user = orm.relationship('User')
