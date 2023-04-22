import requests


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


def organization_parameters(organization):
    # передаешь в функцию полученную из запроса организацию
    coord = organization['geometry']['coordinates']
    name = organization['properties']['CompanyMetaData']['name']
    address = organization['properties']['CompanyMetaData']['address']
    hours = organization['properties']['CompanyMetaData']['text']
    phone = organization['properties']['CompanyMetaData']['Phones'][0]['formatted']
    # координаты (в виде списка из двух строк), название, адрес, часы работы, телефон
    return [coord, name, address, hours, phone]


def work_with_request(request):
    # тут начинается твоя работа
    pass