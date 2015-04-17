# coding=utf-8
from collections import deque

import helpers


_host = 'http://www.parliament.mn'
_main_url = '{host}//en/who?type=3'.format(host=_host)

POL_POS = 'political_position'
ADD_POL_POS = '!political_position'
PER_NAME = 'person_name'
PIC_URL = 'picture_url'
PERSON_URL = 'url'


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


def custom_opener(url, linux=True):
    """
    While using WINDOWS use linux=False parameter, but before final contribute change in to linux=True
    :param url: input url
    :param linux: switch between linux or windows
    """
    from bs4 import BeautifulSoup
    from helpers import fetch_string

    if linux:
        return BeautifulSoup(fetch_string(url, cache_hours=6))
    else:
        from urllib2 import urlopen

        try:
            return BeautifulSoup(urlopen(url).read())
        except Exception, e:
            print e
            pass


def get_all_persons(url):
    persons = []
    main_page = custom_opener(url, linux=True)

    for row in main_page.find('div', {'class': 'span9'}).find_all('div', {'class': 'row'}):
        frames = row.find_all('a')

        for _row in frames:
            if _row:
                person_url = _host + _row.get('href')
                person_picture = _host + _row.find('img').get('src')
                data = deque([x.strip() for x in _row.find('div', {'class': 'cvListItem'}).text.split('\n')])
                person_name = data.popleft()
                obj = {
                    PERSON_URL: person_url,
                    PIC_URL: person_picture,
                    PER_NAME: person_name,
                    POL_POS: data.popleft()
                }

                if data:
                    obj.update({ADD_POL_POS: data.pop()})

                persons.append(obj)

    return persons


def get_entities(persons):
    entities = []
    for person in persons:
        name = person[PER_NAME]
        values = person.values()
        unique_id = create_id([_.encode('utf-8') for _ in values])

        fields = [
            {'tag': t.strip('!'), 'value': v} for t, v in person.items()
        ]

        entities.append(create_entity(unique_id, 'person', name, fields))

    return entities


def main():
    main_obj = get_all_persons(_main_url)

    for entity in get_entities(main_obj):
        # helpers.check(entity)

        helpers.emit(entity)

# main scraper
if __name__ == "__main__":
    main()
