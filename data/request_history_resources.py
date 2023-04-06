from flask import jsonify
from flask_restful import abort, Resource

from data import db_session2
from data.request_history import RequestHistory
from data.reqparse_request_history import parser


def abort_if_request_history_not_found(request_history_id_user):
    # проверка, что по запросу что-то найдется
    session = db_session2.create_session()
    request = session.query(RequestHistory).get(request_history_id_user)
    if not request:
        abort(404, message=f"Request_user_id {request_history_id_user} not found")


class RequestHistoryResource(Resource):
    def get(self, request_history_user_id):
        # поиск по id пользователя (мы решили, что оставим только это)
        abort_if_request_history_not_found(request_history_user_id)
        session = db_session2.create_session()
        request_history = session.query(RequestHistory).filter(RequestHistory.user_id
                                                             == request_history_user_id)
        return jsonify({'request_history': [item.to_dict(
            only=('user_id', 'created_date', 'question', 'answer')) for item in request_history]})

    def delete(self, request_history_id):
        # удаление только по id (думаю можно хранить не больше n-ого кол-ва запросов)
        abort_if_request_history_not_found(request_history_id)
        session = db_session2.create_session()
        session.query(RequestHistory).get(request_history_id).delete()
        session.commit()
        return jsonify({'success': 'OK'})


class RequestHistoryListResource(Resource):
    def get(self):
        # получение всех объектов
        session = db_session2.create_session()
        request_history = session.query(RequestHistory).all()
        return jsonify({'request_history': [item.to_dict(
            only=('user_id', 'created_date', 'question', 'answer')) for item in request_history]})

    def post(self):
        # создание нового элемента
        # (обязательно указать id пользователя, дата указывается по умолчанию, но при желании можно и передать,
        # запрос и ответ системы)
        args = parser.parse_args()
        session = db_session2.create_session()
        request_history = RequestHistory(
            user_id=args['user_id'],
            created_date=args['created_date'],
            question=args['question'],
            answer=args['answer'])
        session.add(request_history)
        session.commit()
        return jsonify({'success': 'OK'})
