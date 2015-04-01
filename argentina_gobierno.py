import hashlib
import re

from bs4 import BeautifulSoup

import helpers


_site_ulr = 'http://www.lapampa.gov.ar'
_base_url = '{}/autoridades-xmap.html'.format(_site_ulr)

CUSTOM_TAG = 'political_institute'
POSITION = 'political_position'


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
    return bs.text.strip().encode('utf-8')


def _create_id(args):
    """
    Generate ID for entity
    :param args: strings
    :return: hashsum
    """
    if not isinstance(args, list):
        args = [args]
    conc_names = ''.join(args)
    return hashlib.sha224((re.sub("[^a-zA-Z0-9]", "", conc_names))).hexdigest()


def get_tables(url):
    objects = {'objects': []}
    main_page = BeautifulSoup(helpers.fetch_string(url, cache_hours=6))
    # main_page = BeautifulSoup(urlopen(url))
    tables = main_page.find_all('table')

    def __fill_helper(_tag):
        table_object['instance'].append({CUSTOM_TAG: _bs_to_utf(_tag), 'people': []})

    for table in tables:
        table_object = {'instance': []}
        rows = table.find_all('tr')
        for row in rows:
            tds = row.find_all('td')
            len_tds = len(tds)

            if len_tds:
                if len_tds > 1:
                    p_name = _bs_to_utf(tds[1])
                    p_name = re.sub("^\s+", "", p_name.split(".")[-1])
                    person_info = {POSITION: _bs_to_utf(tds[0]), 'person_name': p_name}
                    if tds[0].find('a'):
                        person_info.update({'person_url': _site_ulr + tds[0].find('a')['href']})
                        if CUSTOM_TAG in table_object['instance'][-1]:
                            table_object['instance'][-1]['people'].append(person_info)
                else:
                    __fill_helper(tds[0])
            else:
                __fill_helper(row)

        objects['objects'].append(table_object)

    return objects


def get_entities(table_obj):
    entities = []

    for table in table_obj['objects']:
        for _entity in table['instance']:
            entity_type = 'person'
            inst = _entity[CUSTOM_TAG]
            q_people = len(_entity['people'])
            if q_people:
                for pers in _entity['people']:

                    if POSITION in pers and 'person_name' in pers:
                        print pers['person_name']

                        _id = _create_id([inst, pers[POSITION], pers['person_name']])

                        fields = [{'tag': CUSTOM_TAG, 'value': inst},
                                  {'tag': POSITION, 'value': pers[POSITION]},
                                  {'tag': 'person_url', 'value': pers['person_url']},
                                  {'tag': 'person_name', 'value': pers['person_name']}]
                        entities.append(_create_entity(_id, entity_type, pers['person_name'], fields))
                    else:
                        raise Exception('problem with {}'.format(pers))
            else:
                _id = _create_id([_entity[CUSTOM_TAG]])

                entities.append(_create_entity(_id, 'organisation', _entity[CUSTOM_TAG],
                                               [{'tag': CUSTOM_TAG, 'value': _entity[CUSTOM_TAG]}]))

    return entities


def main():
    main_obj = get_tables(_base_url)

    for entity in get_entities(main_obj):
        helpers.check(entity)
        # helpers.emit(entity)

# main scraper
if __name__ == "__main__":
    main()
