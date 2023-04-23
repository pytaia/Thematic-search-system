# Класс для структурирования вывода параметров запросов по организациям и поиску топонимов
# ( + применение в уточняющих запросах пользователей - развиваемые функционеальные возможности)
class Request_parameters():
    def __init__(self, data, type):
        self.type = type
        self.coord = data['geometry']['coordinates']
        if self.type == 'CompanyMetaData':
            self.name = data['properties']['CompanyMetaData']['name']
            self.address = data['properties']['CompanyMetaData']['address']
            self.hours = data['properties']['CompanyMetaData']['text']
            self.phone = list(map(lambda phone: phone['formatted'], data['properties']['CompanyMetaData']['Phones']))
            self.categories = list(
                map(lambda category: category['name'], data['properties']['CompanyMetaData']['Categories']))
            self.url = data['properties']['CompanyMetaData']['url']
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
    json_response = response.json()
    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    toponym_coodrinates = toponym["Point"]["pos"]
    coord = ','.join(toponym_coodrinates.split(" "))
    return coord


def complex_language_condition(morph_params):
    return any([elem in morph_params for elem in
                ['NOUN', 'ADJF', 'ADJS', 'VERB', 'INFN', 'NUMB', 'NUMR', 'Hypo', 'Abbr', 'Name', 'Surn', 'Patr', 'Geox',
                 'Orgn', 'Trad', 'UNKN', 'LATN']]) and all([elem not in morph_params for elem in
                                                            ['PRED', 'COMP', 'CONJ', 'PRCL', 'INTJ', 'Qual', 'Cmp2',
                                                             'V-ej', 'Erro', 'NPRO']])
