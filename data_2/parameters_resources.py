from flask import jsonify
from flask_restful import abort, Resource

from data_2 import db_session1
from data_2.parameters import Parameters
from data_2.reqparse_parameters import parser


def abort_if_parameters_not_found(parameters_name_or_id):
    # проверка, что по запросу что-то найдется
    session = db_session1.create_session()
    if parameters_name_or_id.isdigit():
        parameters = session.query(Parameters).get(parameters_name_or_id)
    else:
        parameters = session.query(Parameters).filter(Parameters.name_param.
                                                      like(f'%{parameters_name_or_id}%'))
    if not parameters:
        abort(404, message=f"Parameters_name {parameters_name_or_id} not found")


class ParametersResource(Resource):
    def get(self, parameters_name):
        # поиск по названию критерия (пока только по так, будет нужно по id допишу)
        abort_if_parameters_not_found(parameters_name)
        session = db_session1.create_session()
        parameters = session.query(Parameters).filter(Parameters.name_param.
                                                         like(f'%{parameters_name}%'))
        return jsonify({'parameters': [item.to_dict(
            only=('name_param', 'keys')) for item in parameters]})

    def delete(self, parameters_id):
        # удаление только по id, но думаю эта функция не пригодится
        abort_if_parameters_not_found(parameters_id)
        session = db_session1.create_session()
        session.query(Parameters).get(parameters_id).delete()
        session.commit()
        return jsonify({'success': 'OK'})


class ParametersListResource(Resource):
    def get(self):
        # получение всех объектов
        session = db_session1.create_session()
        parameters = session.query(Parameters).all()
        return jsonify({'parameters': [item.to_dict(
            only=('name_param', 'keys')) for item in parameters]})

    def post(self):
        # создание нового элемента (обязательно указать название и ключи)
        args = parser.parse_args()
        session = db_session1.create_session()
        parameters = Parameters(
            name_param=args['name_param'],
            keys=args['keys'])
        session.add(parameters)
        session.commit()
        return jsonify({'success': 'OK'})
