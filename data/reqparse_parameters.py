from flask_restful import reqparse

# парсер аргументов для базы с параметрами
parser = reqparse.RequestParser()
parser.add_argument('name_param', required=True, type=str)
parser.add_argument('keys', required=True, type=str)