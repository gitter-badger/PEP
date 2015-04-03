# coding=utf-8

import hashlib
import re

from bs4 import BeautifulSoup

import helpers

_main_url = 'http://www.bajacalifornia.gob.mx/portal/gobierno/gabinete.jsp'
_second_url = 'http://www.bajacalifornia.gob.mx/portal/gobierno/gabinete_ampliado.jsp'
_tel_index = re.compile('\([0-9]{3,4}\)')

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


def get_rows(urls):
    print urls
    objects = []
    from pprint import pprint
    main_page = BeautifulSoup(helpers.fetch_string(urls[0], cache_hours=6))
    other_page = BeautifulSoup(helpers.fetch_string(urls[1], cache_hours=6))
    from urllib2 import urlopen

    # main_page = BeautifulSoup(urlopen(urls[0]))

    other_page = BeautifulSoup(urlopen(urls[1]))

    main_rows = main_page.find_all('table', {'cellpadding': "0", 'cellspacing': "1", 'width': "100%"})[1:]
    # pprint([_.text.strip() for _ in main_rows])


    for row in main_rows:
        print '='*10
        trs = row.find_all('tr')
        for tr in trs:
            tr_to_text = _bs_to_utf(tr)

            if not '@' in tr_to_text or not 'Teléfono' in tr_to_text or not 'Teleféno' in tr_to_text:
                print tr_to_text



        # political_position, person_name = row[:2]
        # obj = {'political_position': _bs_to_utf(political_position),
        #        'picture_url': _bs_to_utf(person_name)}
        # objects.append(obj)

    print objects
    return objects


def get_entities(persons):
    entities = []
    for person in persons:
        name = person['name']
        logo = person['picture_url']
        unique_id = _create_id([name, logo])
        fields = [{'tag': 'person_name', 'value': name}, {'tag': 'picture_url', 'value': logo}]
        entities.append(_create_entity(unique_id, 'person', name, fields))
    return entities


def main():
    main_obj = get_rows([_main_url, _second_url])

    for entity in get_entities(main_obj):
        # helpers.check(entity)
        print entity
        helpers.emit(entity)

# main scraper
if __name__ == "__main__":
    main()
