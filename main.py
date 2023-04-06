from flask import Flask
from flask_restful import Api


from data import db_session1, db_session2
from data import organizations_resources, parameters_resources
from data import request_history_resources, user_data_resources

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app)


def main():
    db_session1.global_init("db/goods_and_services.db")
    db_session2.global_init("db/system_users.db")
    # квест не запутаться в этом:
    api.add_resource(organizations_resources.OrganizationsListResource, '/api/v2/organizations')
    api.add_resource(organizations_resources.OrganizationsResource, '/api/v2/organizations/<name_or_id>')
    api.add_resource(parameters_resources.ParametersListResource, '/api/v2/parameters')
    api.add_resource(parameters_resources.ParametersResource, '/api/v2/parameters/<name_or_id>')
    api.add_resource(request_history_resources.RequestHistoryListResource, '/api/v2/request')
    api.add_resource(request_history_resources.RequestHistoryResource, '/api/v2/request/<int:user_id_or_id>')
    api.add_resource(user_data_resources.UserDataListResource, '/api/v2/user')
    api.add_resource(user_data_resources.UserDataResource, '/api/v2/user/<login_or_id>')
    app.run()


if __name__ == '__main__':
    main()