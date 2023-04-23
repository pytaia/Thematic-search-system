from flask import Flask
from flask_restful import Api

from data import db_session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app)


def main():
    db_session.global_init("db/system_users.db")


if __name__ == '__main__':
    main()