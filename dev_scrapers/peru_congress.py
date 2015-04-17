# coding=utf-8

import hashlib
import re

from bs4 import BeautifulSoup

import helpers


_main_url = 'http://www4.congreso.gob.pe/_ingles/lista_pleno.htm'

OFFICE = 'office'
POL_POS = 'political_position'
PER_NAME = 'person_name'
DEP = 'department_name'
PER_URL = 'url'
PIC_URL = 'picture_url'
IMAGE = '/imagenes/top.jpg'


def _custom_opener(url, linux=False):
    if linux:
        return BeautifulSoup(helpers.fetch_string(url, cache_hours=6))
    else:
        from urllib2 import urlopen

        return BeautifulSoup(urlopen(url))


def _create_entity(_id, entity_type, obj_name, fields):
    """
    easy create entity using input data

    :param _id: unique id of entity
    :param entity_type: organisation | person etc
    :param obj_name: formal name
    :param fields: list with {tags and values}
    :return: dict
    """
    return {
        "_meta": {
            "id": _id,
            "entity_type": entity_type
        },
        "name": obj_name,
        "fields": fields
    }


def _bs_to_utf(bs):
    """
    Convert bs4 object to encoded value
    :param bs: bs object
    :return: unicode
    """
    return bs.text.strip()


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


def get_rows(url):
    _container = []
    main_page = _custom_opener(url, True)
    main_rows = main_page.find('tbody').find_all('tr')

    for row in main_rows:
        link = row.find('a')
        if link:
            obj = {PER_URL: link['href'].replace('.htm', '/cargos.asp').replace('www', 'www4'),
                   PIC_URL: link['href'].replace('.htm', IMAGE).replace('www', 'www4'), PER_NAME: _bs_to_utf(link)}
            _container.append(obj)

    return _container


def get_entities(objects):
    entities = []
    for person in objects:
        person_name = person[PER_NAME]
        direct_url = person[PER_URL]
        pic_uri = person[PIC_URL]

        tags = [PER_NAME, PIC_URL, PER_URL]
        values = [person_name, pic_uri, direct_url]
        unique_id = _create_id([_.encode('utf-8') for _ in values])
        fields = [
            {'tag': t, 'value': v} for t, v in zip(tags, values)
        ]

        entities.append(_create_entity(unique_id, 'person', person_name, fields))

    return entities


def main():
    main_obj = get_rows(_main_url)
    for entity in get_entities(main_obj):
        # helpers.check(entity)
        helpers.emit(entity)

# main scraper
if __name__ == "__main__":
    main()
