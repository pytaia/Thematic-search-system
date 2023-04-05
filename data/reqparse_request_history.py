from flask_restful import reqparse
from datetime import datetime

parser = reqparse.RequestParser()
parser.add_argument('user_id', required=True, type=int)
parser.add_argument('created_date', required=True, type=datetime, default=datetime.now())
parser.add_argument('question', required=True, type=str)
parser.add_argument('answer', required=True, type=str)
