from flask import jsonify
from flask_restful import abort, Resource

from data import db_session1
from data.organizations import Organizations
from data_2.reqparse_organizations import parser


def abort_if_organizations_not_found(organizations_name_or_id):
    # проверка, что по запросу что-то найдется
    session = db_session1.create_session()
    if organizations_name_or_id.isdigit():
        organizations = session.query(Organizations).get(organizations_name_or_id)
    else:
        organizations = session.query(Organizations).filter(Organizations.name.
                                                            like(f'%{organizations_name_or_id}%'))
    if not organizations:
        abort(404, message=f"Organizations_name {organizations_name_or_id} not found")


class OrganizationsResource(Resource):
    def get(self, organizations_name):
        # поиск по типу организации (пока только по типу (name), будет нужно по id допишу)
        abort_if_organizations_not_found(organizations_name)
        session = db_session1.create_session()
        organizations = session.query(Organizations).filter(Organizations.name.
                                                            like(f'%{organizations_name}%'))
        return jsonify({'organizations': [item.to_dict(
            only=('name', 'request_about')) for item in organizations]})

    def delete(self, organizations_id):
        # удаление только по id, так как по тип организации может выдать не одно значение
        abort_if_organizations_not_found(organizations_id)
        session = db_session1.create_session()
        session.query(Organizations).get(organizations_id).delete()
        session.commit()
        return jsonify({'success': 'OK'})


class OrganizationsListResource(Resource):
    def get(self):
        # получение всех объектов (хотя это маловероятно пригодится)
        session = db_session1.create_session()
        organizations = session.query(Organizations).all()
        return jsonify({'organizations': [item.to_dict(
            only=('name', 'request_about')) for item in organizations]})

    def post(self):
        # создание нового элемента (обязательно указать тип и запрос)
        args = parser.parse_args()
        session = db_session1.create_session()
        organizations = Organizations(
            name=args['name'],
            request_about=args['request_about'])
        session.add(organizations)
        session.commit()
        return jsonify({'success': 'OK'})
