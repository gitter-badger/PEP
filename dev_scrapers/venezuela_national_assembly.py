# coding=utf-8
from utils import custom_opener, create_entity, create_id
import helpers
import re


_BASE_URL = "http://www.asambleanacional.gob.ve/diputado/ajaxcargardiputados/tipodiputado/{type}"
_DOMAIN = "http://www.asambleanacional.gob.ve"
_PARTIES = {}
WHITESPACE_PATTERN = re.compile('[\t\r\n\v]| {2,}| $|^ ')


def get_all_persons():
    persons = []
    for person_type in range(1, 3):
        url = _BASE_URL.format(type=person_type)
        persons += scrape_type(url)

    return persons


def scrape_type(url_temp):
    result = []
    page_number_temp = url_temp + "/page/{page}"
    for page in range(1, 15):
        result += scrape_page(page_number_temp.format(page=page))

    return result


def scrape_page(url):
    _page = custom_opener(url)
    persons = []
    for person in _page.find_all('td', {'class': 'link'}):
        name = person.find('a', {'id': 'linkdiputado'})
        image = person.find('img')
        attributes = {}
        person_url = get_url(name.get('href'))

        for attr in person.find_all('a', {'id': 'linkestado'}):
            key, value = attr.text.split(':')
            attributes[key] = value

        if name and image:
            obj = {
                'url': person_url,
                'picture_url': get_url(image.get('src')),
                'person_name': name.text,
                'political_party': get_party_name(attributes['Partido'], person_url),
                'political_region': attributes['Estado']
            }
            persons.append(obj)

    return persons

def get_party_name(party, url):
    if party in _PARTIES.keys():
        return _PARTIES[party]

    _page = custom_opener(url)
    for info in _page.find_all('div', {'id': 'datos2'}):
        content = info.text
        if party in content:
            string = '\({0}\)'.format(party)
            party_name = re.sub(string, '', content)
            _PARTIES[party] = WHITESPACE_PATTERN.sub('', party_name)
            return party_name

    return party

def get_url(string):
    if not string.startswith(_DOMAIN):
        string = _DOMAIN + string

    return string


def get_entities(persons):
    entities = []
    for person in persons:
        name = person.pop('person_name')
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
        # helpers.emit(entity)
        helpers.check(entity)

# main scraper
if __name__ == "__main__":
    main()
