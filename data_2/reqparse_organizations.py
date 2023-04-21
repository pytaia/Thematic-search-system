from flask_restful import reqparse

# парсер аргументов для базы с организациями
parser = reqparse.RequestParser()
parser.add_argument('name', required=True, type=str)
parser.add_argument('request_about', required=True, type=str)