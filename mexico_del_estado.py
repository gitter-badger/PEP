# coding=utf-8

import hashlib
import re

from bs4 import BeautifulSoup

import helpers

_main_url = 'http://www.colima-estado.gob.mx/d/tema.php?iw=MTI4Mg=='

POL_POS = 'political_position'
PER_NAME = 'person_name'
PIC = 'picture_url'


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
    main_page = BeautifulSoup(helpers.fetch_string(url, cache_hours=6))
    main_rows = main_page.find('table', {'cellpadding': "0", 'cellspacing': "1", 'width': "98%"}).find_all('tr')

    objects = []

    for _r in main_rows:
        sub_td = _r.find_all('td')

        for td in sub_td:
            if _bs_to_utf(td):

                image = td.find('img')['src']
                person_name = None
                political_position = None

                if len(td.find_all('strong')) > 1:
                    person_name, political_position = [_bs_to_utf(_) for _ in td.find_all('strong')]

                else:
                    if td.find('a'):
                        links = td.find_all('a')
                        for link in links:
                            if link and link.text.startswith('Curriculum'):
                                link.extract()
                        link = td.find('a')
                        political_position = _bs_to_utf(link.extract())
                        person_name = ' '.join([_ for _ in _bs_to_utf(td).split('\n') if _])

                obj = {PER_NAME: person_name, POL_POS: political_position, PIC: image}
                objects.append(obj)

    return objects


def get_entities(persons):
    entities = []
    for person in persons:
        name = person[PER_NAME]
        position = person[POL_POS]
        image = person[PIC]

        tags = [PER_NAME, POL_POS, PIC]
        values = [name, position, image]

        unique_id = _create_id([_.encode('utf-8') for _ in values])

        fields = [
            {'tag': t, 'value': v} for t, v in zip(tags, values)
        ]

        entities.append(_create_entity(unique_id, 'person', name, fields))

    return entities


def main():
    main_obj = get_rows(_main_url)
    for entity in get_entities(main_obj):
        # helpers.check(entity)
        helpers.emit(entity)

# main scraper
if __name__ == "__main__":
    main()
