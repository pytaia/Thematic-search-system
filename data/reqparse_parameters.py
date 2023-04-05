from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument('name_param', required=True, type=str)
parser.add_argument('keys', required=True, type=str)