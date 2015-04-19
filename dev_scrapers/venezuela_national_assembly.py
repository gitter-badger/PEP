# coding=utf-8
from utils import custom_opener, create_entity, create_id
import helpers
import platform


_BASE_URL = "http://www.asambleanacional.gob.ve/diputado/ajaxcargardiputados/tipodiputado/{type}"
_DOMAIN = "http://www.asambleanacional.gob.ve"
_OS_LINUX = True if "linux" in platform.system().lower() else False


# TEST_DATA = '''
# Rule Name	Rule Value
# Scrape minimum number of entities	40
# Contains given name or AKA entry, special field "name: person_name" field	Ulziisaikhan ENKHTUVSHIN
# Contains a field with "tag": "url", where the value is the url of the page containing person data	http://www.parliament.mn/en/who?type=3&cid=78
# Contains a field "tag": "picture_ul", with the value being the url of a picture on page	http://www.parliament.mn/en/files/images/824-7864481.jpg
# Contains a field "tag": "political_position", where value is given political position	Member of the State Great Hural (Parliament) of Mongolia
# Contains given name or AKA entry, special field "name: person_name" field	Zandaakhuu ENKHBOLD
# Contains a field "tag": "political_position", where value is given political position	Chairman of the State Great Hural (Parliament) of Mongolia
# Contains a field "tag": "picture_ul", with the value being the url of a picture on page	http://www.parliament.mn/en/files/images/658-7864481.jpg
# Scrape minimum number of entities	30
# Contains a field "tag": "political_position", where value is given political position	Vice Chairman of the State Great Hural (Parliament) of Mongolia
# '''


def get_all_persons():
    persons = []
    for type in range(1,3):
        url = _BASE_URL.format(type=type)
        persons += scrape_type(url)

    return persons

def scrape_type(url_temp):
    result = []
    page_number_temp = url_temp + "/page/{page}"
    for page in range(1, 15):
        result += scrape_page(page_number_temp.format(page=page))

    return result

def scrape_page(url):
    _page = custom_opener(url, linux=_OS_LINUX)
    persons = []
    for person in _page.find_all('td', {'class': 'link'}):
        name = person.find('a', {'id': 'linkdiputado'})
        image = person.find('img')
        attributes = {}
        for attr in person.find_all('a', {'id': 'linkestado'}):
            key, value = attr.text.split(':')
            attributes[key] = value

        if name and image:
            obj = {
                'url': get_url(name.get('href')),
                'picture_url': get_url(image.get('src')),
                'person_name': name.text,
                'political_party': attributes['Partido'],
                'political_region': attributes['Estado']
            }
            persons.append(obj)

    return persons

def get_url(string):
    if not string.startswith(_DOMAIN):
        string = _DOMAIN + string

    return string

def get_entities(persons):
    entities = []
    for person in persons:
        name = person['person_name']
        values = person.values()
        unique_id = create_id([_.encode('utf-8') for _ in values])

        fields = [
            {'tag': t, 'value': v} for t, v in person.items()
        ]

        entities.append(create_entity(unique_id, 'person', name, fields))

    return entities


def main():
    main_obj = get_all_persons()

    for entity in get_entities(main_obj):
        helpers.emit(entity)

# main scraper
if __name__ == "__main__":
    main()
