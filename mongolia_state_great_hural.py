# coding=utf-8
from collections import deque
import hashlib
import re

from bs4 import BeautifulSoup

import helpers


_host = 'http://www.parliament.mn'
_main_url = '{host}//en/who?type=3'.format(host=_host)

POL_POS = 'political_position'
ADD_POL_POS = '!political_position'
PER_NAME = 'person_name'
PIC_URL = 'picture_url'
PERSON_URL = 'url'


'''
Rule Name	Rule Value
Scrape minimum number of entities	40
Contains given name or AKA entry, special field "name: person_name" field	Ulziisaikhan ENKHTUVSHIN
Contains a field with "tag": "url", where the value is the url of the page containing person data	http://www.parliament.mn/en/who?type=3&cid=78
Contains a field "tag": "picture_ul", with the value being the url of a picture on page	http://www.parliament.mn/en/files/images/824-7864481.jpg
Contains a field "tag": "political_position", where value is given political position	Member of the State Great Hural (Parliament) of Mongolia
Contains given name or AKA entry, special field "name: person_name" field	Zandaakhuu ENKHBOLD
Contains a field "tag": "political_position", where value is given political position	Chairman of the State Great Hural (Parliament) of Mongolia
Contains a field "tag": "picture_ul", with the value being the url of a picture on page	http://www.parliament.mn/en/files/images/658-7864481.jpg
Scrape minimum number of entities	30
Contains a field "tag": "political_position", where value is given political position	Vice Chairman of the State Great Hural (Parliament) of Mongolia
'''

def _create_entity(_id, entity_type, obj_name, fields, aka=False):
    """
    easy create entity using input data

    :param _id: unique id of entity
    :param entity_type: organisation | person etc
    :param obj_name: formal name
    :param fields: list with {tags and values}
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
        # {'aka': 'name': '??'}
        default.update({'aka': [aka]})
    return default


def _create_id(args):
    """
    Generate ID for entity
    :param args: strings
    :return: hashsum
    """
    if not isinstance(args, list):
        args = [args]
    conc_names = ''.join([_.decode('utf-8') for _ in args])
    return hashlib.sha224((re.sub("[^a-zA-Z0-9]", "", conc_names))).hexdigest()


def _custom_opener(url, linux=True):
    if linux:
        return BeautifulSoup(helpers.fetch_string(url, cache_hours=6))
    else:
        from urllib2 import urlopen

        try:
            return BeautifulSoup(urlopen(url).read())
        except Exception, e:
            print e
            pass


def get_all_persons(url):
    persons = []
    main_page = _custom_opener(url, linux=True)

    for row in main_page.find('div', {'class': 'span9'}).find_all('div', {'class': 'row'}):
        frames = row.find_all('a')

        if len(frames) > 1:
            first_in_row, second_in_row = row.find_all('a')
        else:
            second_in_row = None
            first_in_row = frames.pop()

        for _row in [first_in_row, second_in_row]:
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
        unique_id = _create_id([_.encode('utf-8') for _ in values])

        fields = [
            {'tag': t.strip('!'), 'value': v} for t, v in person.items()
        ]

        entities.append(_create_entity(unique_id, 'person', name, fields))

    return entities


def main():
    main_obj = get_all_persons(_main_url)

    for entity in get_entities(main_obj):
        # helpers.check(entity)

        helpers.emit(entity)

# main scraper
if __name__ == "__main__":
    main()
