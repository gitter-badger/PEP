# coding=utf-8
import re

from bs4 import BeautifulSoup
from dateutil import parser

import helpers


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
    """
    While using WINDOWS use linux=False parameter, but before final contribute change in to linux=True
    :param url: input url
    :param linux: switch between linux or windows
    """

    import platform
    from helpers import fetch_string

    _OS_LINUX = True if "linux" in platform.system().lower() or 'unix' in platform.system().lower() else False

    if _OS_LINUX:
        return BeautifulSoup(fetch_string(url, cache_hours=6))
    else:
        from urllib2 import urlopen

        try:
            return BeautifulSoup(urlopen(url, timeout=20).read())
        except Exception, e:
            print e


_host = 'http://www.apra.gov.au'

URLS = [
    'http://www.apra.gov.au/CrossIndustry/Pages/Disqualification-Register.aspx'
]

ENTITY = 'Entity'
PER_NAME = 'person_name'
DATE = 'Date Effective'
ACT = 'Act & Section'
PRESS = 'Press Release'
DISQUALIFICATION = 'Disqualification'
PERSON_URL = 'url'

WANTED_LIST = [ENTITY, DATE, ACT, PRESS, DISQUALIFICATION]


def get_all_persons(url):
    persons = []
    page = custom_opener(url)
    rows = page.find('table', {'id': 'drTable'}).find_all('tr')

    obj_urls = (_host + row.find('a').get('href') for row in rows)

    for _url in obj_urls:

        person = {PERSON_URL: _url}

        txt_page = str(custom_opener(_url))
        table = BeautifulSoup(
            re.search(r'(<table border="0" cellpadding="1" cellspacing="0".+?</table>)', txt_page).group())

        nested_rows = table.find_all('tr')
        keys = ['Last Name', 'First Name', DISQUALIFICATION, DATE, ACT, ENTITY,
                PRESS]
        for nr in nested_rows:
            key, value = nr.find_all('td')
            _key, _value = key.text.strip(), value.text.strip()

            if _key == keys[0]:
                person[PER_NAME] = _value

            if _key == keys[1]:
                try:
                    person[PER_NAME] = '{f_name} {l_name}'.format(f_name=_value, l_name=person[PER_NAME])
                except UnicodeEncodeError:
                    pass

            for key in keys[2:]:
                if _key == key and _value:
                    person[key] = _value

        persons.append(person)

    return persons


def get_entities(persons):
    entities = []
    for person in persons:
        if person[PER_NAME]:
            name = person.pop(PER_NAME)

            if person[DATE]:
                person[DATE] = str(parser.parse(person[DATE])).split()[0]

            values = person.values()
            unique_id = create_id([_.encode('utf-8') for _ in values])

            fields = []
            for t, v in person.items():
                if t not in WANTED_LIST:
                    fields.append({'tag': t, 'value': v})
                else:
                    fields.append({'name': t, 'value': v})

            entities.append(create_entity(unique_id, 'person', name, fields))
    return entities


def main():
    for url in URLS:
        main_obj = get_all_persons(url)

        for entity in get_entities(main_obj):
            # helpers.check(entity)
            helpers.emit(entity)


# main scraper
if __name__ == "__main__":
    main()
