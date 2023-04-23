from main import main
from data import db_session
from data.request_history import RequestHistory
from speechkit import Session, SpeechSynthesis, ShortAudioRecognition
from datetime import datetime
from system_functions import Request_parameters, complex_language_condition, address_is_true
from random import choice
import requests
import wikipedia
from branching_bot_responses import speech_synthesis_Company
import pymorphy2
import re


class Multiple_analysis():
    def __init__(self, user_request, user_id):
        # Переменные состояния, типа и статуса обрабатываемого запроса
        self.user_request = user_request
        self.boolean_result = True
        self.type_requests = None
        self.type_output = 'text'
        self.wiki_bool = False

        self.data_request = []

        # Подключение базы данных
        main()
        self.db_sess = db_session.create_session()
        self.speech_processing() if isinstance(self.user_request, bytes) else None
        self.user_request = self.user_request.lower()
        self.context_params = RequestHistory(user_id=user_id, created_date=datetime.now(), question=''.join(
            re.split(r'\b', self.user_request)[1::2]), answer=self.boolean_result)

        # Параметры для вывода результатов
        self.map_params = {'l': 'map', 'pt': []}
        self.request_params = {'apikey': "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3",
                      'text': '',
                      'lang': 'ru_RU',
                      'spn': '0.1,0.1'}

        self.session = Session.from_yandex_passport_oauth_token(
            "y0_AgAAAAA2yeshAATuwQAAAADhfdW2-LGBw40LQ36n1MjdFL1dES3pYM0",
            "b1g53mngvuej0gor2tsa")

        self.branching_and_stages()

    def primitive_intent_analysis(self):  # Анализ запроса пользователя, извлечение смысловой части
        morph_base = pymorphy2.MorphAnalyzer()

        # Удаление не относящихся к сущности запроса слов
        self.data_request = [word for word in re.split(r'\b', self.user_request)[1::2] if
                             complex_language_condition(re.split(r'\b', str(morph_base.parse(word)[0].tag))[1::2])]


        self.context_params.question = '&'.join(self.data_request)

        # Поиск дополнительных параметров в вариациях начальных форм слов
        for words in list(map(lambda word: [elem.normal_form for elem in morph_base.parse(word)],
                              re.split(r'\b', self.user_request)[1::2])):
            if any([word in ['гибрид', 'гибридный', 'гибридным', 'смешешанный', 'смешать'] for word in words]):
                self.map_params['l'] = 'sat,skl'
            elif any([word in ['спутник', 'спутниковый', 'спутником'] for word in words]):
                self.map_params['l'] = 'sat'
            elif any([word in ['аудио', 'голос', 'голосовое', 'голосовым', 'голосовой'] for word in words]):
                self.type_output = 'voice'
            elif any([word in ['вики', 'википедия', 'wiki', 'wikipedia'] for word in words]):
                self.wiki_bool = True

    def speech_processing(self):  # Преобразование голосового сообщения в текст
        self.user_request = ShortAudioRecognition(self.session).recognize(self.user_request, format='lpcm',
                                                                          sampleRateHertz=16000)

    def request_history_record(self):  # Сохранение запроса пользователя
        self.db_sess.add(self.context_params)
        self.db_sess.commit()



    def branching_and_stages(self):  # Структура и процесс анализа запроса
        try:
            self.primitive_intent_analysis()
            self.search_adjusted_parameters()
            self.request_history_record()
        except Exception:
            self.boolean_result = False
            self.context_params.answer = False
            self.request_history_record()

    def search_adjusted_parameters(self):  # Запрос по найденым намерениям в запросе пользователя
        self.request_params['text'] = ' '.join(self.data_request)
        self.search_parameters = requests.get("https://search-maps.yandex.ru/v1/", self.request_params).json()[
            'features']

        self.type_requests = 'Company' if 'CompanyMetaData' in self.search_parameters[0][
            'properties'].keys() else 'Geocoder'

    def analysis_result_output(self):  # Формирование вывода
        if address_is_true(' '.join(self.data_request)):
            description = [params.output_params() for params in
                           [Request_parameters(result, self.type_requests) for result in self.search_parameters]]

            for elem in [Request_parameters(result, self.type_requests) for result in self.search_parameters]:
                self.map_params['pt'].append(','.join(list(map(str, elem.coord))))
            if len(self.map_params['pt']) == 1:
                self.map_params['ll'] = self.map_params['pt'][0]
                self.map_params['z'] = 16
            if self.type_output == 'voice':
                description = SpeechSynthesis(self.session).synthesize_stream(
                    text='. '.join([choice(speech_synthesis_Company)]),
                    voice='zahar', format='lpcm', sampleRateHertz=16000)
            return self.map_params, description, self.wiki_data_response(description, True)
        else:
            return {}, [], self.wiki_data_response(self.data_request, False, extra=True)

    def wiki_data_response(self, description, param, extra=False):
        wiki_data = []
        if self.wiki_bool or extra:
            wikipedia.set_lang('ru')
            if param:
                try:
                    for elem in list(map(lambda x: x[4], description)):
                        if 'вики' not in elem and 'wiki' not in elem:
                            wiki_data.append([wikipedia.search(elem)[0], wikipedia.page(elem).url])
                except Exception:
                    pass
            else:
                try:
                    for elem in self.data_request:
                        if 'вики' not in elem and 'wiki' not in elem:
                            wiki_data.append([wikipedia.search(elem)[0], wikipedia.page(elem).url])
                except Exception:
                    pass
        return wiki_data
