# coding=utf-8

import hashlib
import re

from bs4 import BeautifulSoup

import helpers

_main_url = 'http://www.chiapas.gob.mx/funcionarios/estatal/ejecutivo'

OFFICE = 'office'
POL_POS = 'political_position'
PER_NAME = 'person_name'
DEP = 'department_name'
PER_URL = 'url'


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
    main_page = _custom_opener(url)
    main_rows = main_page.find('div', {'class': "ser-cont", 'id': "resultado"})
    for i, v in zip(main_rows.find_all('h2'), main_rows.find_all('ul')):

        for obj in [{DEP: _bs_to_utf(i), OFFICE: _bs_to_utf(_), PER_URL: _main_url + _.find('a')['href'].strip('ejecutivo')} for _ in v]:
            _container.append(obj)

    return _container


def get_entities(objects):
    entities = []
    for person in objects:
        office = person[OFFICE]
        direct_url = person[PER_URL]
        dep_name = person[DEP]

        sub_page = _custom_opener(direct_url)

        try:
            h1s = sub_page.find('div', {'class': 'N2'}).find_all('h1')
            name, pos = h1s
            try:
                person_name = _bs_to_utf(name)
                if person_name:
                    pol_pos = _bs_to_utf(pos)

                    tags = [OFFICE, PER_NAME, POL_POS, PER_URL, DEP]
                    values = [office, person_name, pol_pos, direct_url, dep_name]

                    unique_id = _create_id([_.encode('utf-8') for _ in values])

                    fields = [
                        {'tag': t, 'value': v} for t, v in zip(tags, values)
                    ]
                    p_name = re.sub("^\s+", "", person_name.split(".")[-1].strip())
                    entities.append(_create_entity(unique_id, 'person', p_name, fields))
            except:
                continue
        except:
            continue

    return entities


def main():
    main_obj = get_rows(_main_url)
    for entity in get_entities(main_obj):
        # helpers.check(entity)
        helpers.emit(entity)

# main scraper
if __name__ == "__main__":
    main()
