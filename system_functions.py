import requests

# Класс для структурирования вывода параметров запросов по организациям и поиску топонимов
# ( + применение в уточняющих запросах пользователей - развиваемые функционеальные возможности)
class Request_parameters():
    def __init__(self, data, type):
        self.type = type
        self.coord = data['geometry']['coordinates']
        if self.type == 'Company':
            self.name = data['properties']['CompanyMetaData']['name']
            self.address = data['properties']['CompanyMetaData']['address']
            self.hours = data['properties']['CompanyMetaData']['Hours']['text'] \
                if 'Hours' in data['properties']['CompanyMetaData'].keys() else ''
            self.phone = list(map(lambda phone: phone['formatted'],
                                  data['properties']['CompanyMetaData']['Phones'])) \
                if 'Phones' in data['properties']['CompanyMetaData'].keys() else ''
            self.categories = list(
                map(lambda category: category['name'], data['properties']['CompanyMetaData']['Categories']))

            self.url = data['properties']['CompanyMetaData']['url'] if 'url' in data['properties'][
                'CompanyMetaData'].keys() else ''
        else:
            self.address = data['properties']['GeocoderMetaData']['text']

    def output_params(self):
        if self.type == 'Company':
            return [self.name, self.address, self.hours, self.phone, self.categories, self.url]
        else:
            return [self.address]


def address_is_true(address):
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": address,
        "format": "json"}
    response = requests.get(geocoder_api_server, params=geocoder_params)
    if not response:
        return False
    return True


def complex_language_condition(morph_params):
    return any([elem in morph_params for elem in
                ['NOUN', 'ADJF', 'ADJS', 'VERB', 'INFN', 'NUMB', 'NUMR', 'Hypo', 'Abbr', 'Name', 'Surn', 'Patr', 'Geox',
                 'Orgn', 'Trad', 'UNKN', 'LATN']]) and all([elem not in morph_params for elem in
                                                            ['PRED', 'COMP', 'CONJ', 'PRCL', 'INTJ', 'Qual', 'Cmp2',
                                                             'V-ej', 'Erro', 'NPRO']])


def getting_an_image(answer):
    map_api_server = f"http://static-maps.yandex.ru/1.x/?"

    if 'll' in answer[0][0]:
        map_api_server += f"ll={answer[0][0]['ll']}&"
    if 'z' in answer[0][0]:
        map_api_server += f"z={answer[0][0]['z']}&"
    map_api_server += f"l={answer[0][0]['l']}&pt={'~'.join([i + ',vkbkm' for i in answer[0][0]['pt']])}"
    if answer[1] == 'Geocoder':
        mess = f"Адрес: {answer[0][1][0][0]}"
    elif answer[1] == 'Company':
        mess = []
        for i in answer[0][1]:
            m = [f'Название: {i[4][0]} {i[0]}', f'Адрес: {i[1]}']
            if i[2]:
                m.append(f'Время работы: {i[2]}')
            if i[3]:
                m.append(f"Номер телефона: {i[3][0]}")
            if i[5]:
                m.append(f'Сайт: {i[5]}')
            mess.append('\n'.join(m))
        mess = '\n\n'.join(mess)
    mess2 = ''
    if answer[0][2]:
        mess2 = '\n\n'.join([f"Тема: {i[0]}" + '\n' + i[1] for i in answer[0][2]])
    return (map_api_server, mess, mess2)