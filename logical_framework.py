from main import main
from data import db_session
from data.request_history import RequestHistory
from speechkit import Session, SpeechSynthesis, ShortAudioRecognition
from datetime import datetime
from system_functions import Request_parameters, complex_language_condition
from random import choice
import requests
from branching_bot_responses import speech_synthesis_Company, speech_synthesis_Geocoder
import pymorphy2
import re


class Multiple_analysis():
    def __init__(self, user_request, user_id):
        self.user_request = user_request
        self.boolean_result = True
        self.type_requests = None
        self.type_output = 'text'

        self.data_request = []

        main()
        self.db_sess = db_session.create_session()
        self.speech_processing() if isinstance(self.user_request, bytes) else None
        self.context_params = RequestHistory(user_id=user_id, created_date=datetime.now(), question=''.join(
            re.split(r'\b', self.user_request)[1::2]), answer=self.boolean_result)

        self.map_params = {'l': 'map', 'pt': []}
        self.request_params = {'apikey': "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3",
                      'text': '',
                      'lang': 'ru_RU',
                      'spn': '0.1,0.1'}

        self.session = Session.from_yandex_passport_oauth_token(
            "y0_AgAAAAA2yeshAATuwQAAAADhfdW2-LGBw40LQ36n1MjdFL1dES3pYM0",
            "b1g53mngvuej0gor2tsa")

        self.branching_and_stages()

    def branching_and_stages(self):
        try:
            self.primitive_intent_analysis()
            self.search_adjusted_parameters()
            self.request_history_record()
        except Exception:
            self.boolean_result = False
            self.request_history_record()

    def primitive_intent_analysis(self):
        morph_base = pymorphy2.MorphAnalyzer()

        self.data_request = [word for word in re.split(r'\b', self.user_request)[1::2] if
                             complex_language_condition(re.split(r'\b', str(morph_base.parse(word)[0].tag))[1::2])]
        self.context_params.question = '&'.join(self.data_request)

        for words in list(map(lambda word: [elem.normal_form for elem in morph_base.parse(word)],
                              re.split(r'\b', self.user_request)[1::2])):
            if any([word in ['гибрид', 'гибридный', 'гибридным', 'смешешанный', 'смешать'] for word in words]):
                self.map_params['l'] = 'sat,skl'
            elif any([word in ['спутник', 'спутниковый', 'спутником'] for word in words]):
                self.map_params['l'] = 'sat'
            elif any([word in ['аудио', 'голос', 'голосовое', 'голосовым', 'голосовой'] for word in words]):
                self.type_output = 'voice'

    def speech_processing(self):
        self.user_request = ShortAudioRecognition(self.session).recognize(self.user_request, format='lpcm',
                                                                          sampleRateHertz=16000)

    def request_history_record(self):
        self.db_sess.add(self.context_params)
        self.db_sess.commit()

    def search_adjusted_parameters(self):
        self.request_params['text'] = ' '.join(self.data_request)
        self.search_parameters = requests.get("https://search-maps.yandex.ru/v1/", self.request_params).json()[
            'features']

        self.type_requests = 'Company' if 'CompanyMetaData' in self.search_parameters[0][
            'properties'].keys() else 'Geocoder'

    def analysis_result_output(self):
        description = [params.output_params() for params in
                       [Request_parameters(result, self.type_requests) for result in self.search_parameters]]
        for elem in [Request_parameters(result, self.type_requests) for result in self.search_parameters]:
            self.map_params['pt'].append(','.join(list(map(str, elem.coord))))
        if len(self.map_params['pt']) == 1:
            self.map_params['ll'] = self.map_params['pt'][0]

        if self.type_output == 'voice':
            description = SpeechSynthesis(self.session).synthesize_stream(
                text='. '.join([choice(speech_synthesis_Company)]),
                voice='zahar', format='lpcm', sampleRateHertz=16000)
            print(description)
        return self.map_params, description


name = Multiple_analysis('аптека по адресу 45 стелковой дивизии 64/2к1', 1)
print(name.analysis_result_output())
