from flask import jsonify
from flask_restful import abort, Resource

from data import db_session2
from data.user_data import UserData
from data.reqparse_user_data import parser


def abort_if_user_data_not_found(user_data_id_or_login):
    # проверка, что по запросу что-то найдется
    session = db_session2.create_session()
    if user_data_id_or_login.isdigit():
        user = session.query(UserData).get(user_data_id_or_login)
    else:
        user = session.query(UserData).filter(UserData.login == user_data_id_or_login)
    if not user:
        abort(404, message=f"User {user_data_id_or_login} not found")


class UserDataResource(Resource):
    def get(self, user_login):
        # поиск по логину (логин ты говорил преобразуешь в строку, т.е. это не должен быть набор цифорок)
        abort_if_user_data_not_found(user_login)
        session = db_session2.create_session()
        user = session.query(UserData).filter(UserData.login == user_login).first()
        return jsonify({'user': user.to_dict(
            only=('login', 'name', 'address'))})

    def delete(self, user_id):
        # удаление только по id, но думаю эта функция не пригодится
        abort_if_user_data_not_found(user_id)
        session = db_session2.create_session()
        session.query(UserData).get(user_id).delete()
        session.commit()
        return jsonify({'success': 'OK'})

    def edit(self):
        # редактирование. сначала регестрируем логин пользователя,
        # потом с ним знакомимся, спрашиваем адрес и т.д.. ищем пользователя,
        # которого надо "исправить" по его логину.
        # я так сделала, потому что в парсере логин обязательный - параметр, и он индивидуальный.
        args = parser.parse_args()
        abort_if_user_data_not_found(args['login'])
        session = db_session2.create_session()
        user = session.query(UserData).filter(UserData.login == args['login']).first()
        if 'name' in args:
            user.name = args['name']
        if 'address' in args:
            user.address = args['address']
        session.commit()
        return jsonify({'success': 'OK'})


class UserDataListResource(Resource):
    def get(self):
        # получение всех объектов
        session = db_session2.create_session()
        users = session.query(UserData).all()
        return jsonify({'request_history': [item.to_dict(
            only=('login',)) for item in users]})

    def post(self):
        # создание нового элемента (указать надо только логин)
        args = parser.parse_args()
        session = db_session2.create_session()
        user = UserData(
            login=args['login'])
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})