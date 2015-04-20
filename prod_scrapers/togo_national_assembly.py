# coding=utf-8
from collections import deque
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


_host = 'http://www.assemblee-nationale.tg'
MAIN_URL = '{host}/spip.php?article17'.format(host=_host)

PER_NAME = 'person_name'
PIC_URL = 'picture_url'
POL_PRT = 'political_party'
SEC_POL_PRT = '!political_party'
PERSON_URL = 'url'

_PARTY_REGEX = re.compile(ur'(\(.+?\))')


def get_all_persons(url):
    persons = []
    main_page = custom_opener(url)

    for even, odd in zip(main_page.find_all('tr', {'class': 'row_even'}),
                         main_page.find_all('tr', {'class': 'row_odd'})):
        img = even.find_all('img')
        text_info = odd.find_all('td')
        for k, v in zip(img, text_info):
            person_image = _host + '/' + k.get('src')
            name = v.text.split('(')[0].strip()
            parties = deque([_.strip('()').lstrip() for _ in re.findall(_PARTY_REGEX, v.text)])
            if not len(parties):
                parties.append('GMP')

            obj = {
                PER_NAME: name,
                PIC_URL: person_image,
                POL_PRT: parties.pop()
            }

            if len(parties):
                obj[SEC_POL_PRT] = parties.pop()
            persons.append(obj)

    return persons


def get_entities(persons):
    entities = []
    for person in persons:
        name = person.pop(PER_NAME)
        values = person.values()
        unique_id = create_id([_.encode('utf-8') for _ in values])

        fields = [
            {'tag': t.strip('!'), 'value': v} for t, v in person.items()
        ]

        entities.append(create_entity(unique_id, 'person', name, fields))
    return entities


def main():
    main_obj = get_all_persons(MAIN_URL)

    for entity in get_entities(main_obj):
        # helpers.check(entity)
        helpers.emit(entity)


# main scraper
if __name__ == "__main__":
    main()
