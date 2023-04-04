from flask import Flask
from data import db_session1
from data import db_session2

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


def main():
    db_session1.global_init("db/goods_and_services.db")
    db_session2.global_init("db/system_users.db")
    app.run()


if __name__ == '__main__':
    main()