from flask import jsonify
from flask_restful import abort, Resource

from data import db_session2
from data.user_data import UserData
from data.reqparse_user_data import parser


def abort_if_user_data_not_found(user_data_id_or_login):
    session = db_session2.create_session()
    if user_data_id_or_login.isdigit():
        user = session.query(UserData).get(user_data_id_or_login)
    else:
        user = session.query(UserData).filter(UserData.login == user_data_id_or_login)
    if not user:
        abort(404, message=f"User {user_data_id_or_login} not found")


class UserDataResource(Resource):
    def get(self, user_login):
        abort_if_user_data_not_found(user_login)
        session = db_session2.create_session()
        user = session.query(UserData).filter(UserData.login == user_login).first()
        return jsonify({'user': user.to_dict(
            only=('login', 'name', 'address'))})

    def delete(self, user_id):
        abort_if_user_data_not_found(user_id)
        session = db_session2.create_session()
        session.query(UserData).get(user_id).delete()
        session.commit()
        return jsonify({'success': 'OK'})

    def edit(self):
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
        session = db_session2.create_session()
        users = session.query(UserData).all()
        return jsonify({'request_history': [item.to_dict(
            only=('login', 'name', 'address')) for item in users]})

    def post(self):
        args = parser.parse_args()
        session = db_session2.create_session()
        user = UserData(
            login=args['login'])
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})