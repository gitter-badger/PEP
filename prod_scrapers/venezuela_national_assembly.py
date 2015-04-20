# coding=utf-8
import re


def create_entity(_id, entity_type, obj_name, fields, aka=False):
    """
    easy create entity using input data

    :param _id: unique id of entity (use create_id(args))
    :param entity_type: (should be string or unicode) organisation | person etc
    :param obj_name: formal name => 'Vasya Pupkin'
    :param fields: list with {tags|names and values} => {'tag': 'political_position', 'value': 'director'}
    :param aka: list with aka names => aka = [{'name': 'Some AKA Name'}, {'name': 'Some AKA Name'}]
    :return: dict
    """
    default = {
        "_meta": {
            "id": _id,
            "entity_type": entity_type
        },
        "name": obj_name,
        "fields": fields
    }

    if aka:
        default.update({'aka': aka})

    return default


def create_id(args):
    """
    Generate ID for entity
    :param args: strings
    :return: hashsum
    """
    from hashlib import sha224
    from re import sub

    if not isinstance(args, list):
        args = [args]
    conc_names = ''.join([_.decode('utf-8') for _ in args])
    return sha224((sub("[^a-zA-Z0-9]", "", conc_names))).hexdigest()


def custom_opener(url):
    import platform

    _OS_LINUX = True if "linux" in platform.system().lower() or 'unix' in platform.system().lower() else False
    """
    While using WINDOWS use linux=False parameter, but before final contribute change in to linux=True
    :param url: input url
    :param linux: switch between linux or windows
    """
    from bs4 import BeautifulSoup
    from helpers import fetch_string

    if _OS_LINUX:
        return BeautifulSoup(fetch_string(url, cache_hours=6))
    else:
        from urllib2 import urlopen

        try:
            return BeautifulSoup(urlopen(url, timeout=20).read())
        except Exception, e:
            print e
            pass


import helpers


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
        helpers.emit(entity)
        # helpers.check(entity)

# main scraper
if __name__ == "__main__":
    main()
