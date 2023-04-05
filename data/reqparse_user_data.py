from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument('login', required=True, type=str)
parser.add_argument('name', required=False, type=str)
parser.add_argument('address', required=False, type=str)