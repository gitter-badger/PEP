import hashlib
import re
from urllib2 import urlopen
from bs4 import BeautifulSoup

import helpers


_site_ulr = 'http://www.lapampa.gov.ar'
_base_url = '{}/autoridades-xmap.html'.format(_site_ulr)
SAFE_QUOTE = ':/?&='

CUSTOM_TAG = 'political_institute'
POSITION = 'political_position'


def _create_entity(_id, entity_type, obj_name, fields):
    return {
        "_meta": {
            "id": _id,
            "entity_type": entity_type
        },
        "name": obj_name,
        "fields": fields
    }


def _bs_to_utf(bs):
    return bs.text.strip().encode('utf-8')


def _create_id(args):
    conc_names = ''.join(args)
    return hashlib.sha224((re.sub("[^a-zA-Z0-9]", "", conc_names))).hexdigest()


def _get_tables(url):
    objects = {'objects': []}
    main_page = BeautifulSoup(helpers.fetch_string(url, cache_hours=6))
    # main_page = BeautifulSoup(urlopen(url))
    tables = main_page.find_all('table')

    for table in tables:
        table_object = {'instance': []}
        rows = table.find_all('tr')
        for row in rows:
            tds = row.find_all('td')
            len_tds = len(tds)

            if len_tds:
                if len_tds > 1:
                    p_name = _bs_to_utf(tds[1])
                    if '.' in p_name:
                        p_name = p_name.split('.')[1].strip()
                    person_info = {POSITION: _bs_to_utf(tds[0]), 'person_name': p_name}
                    if tds[0].find('a'):
                        person_info.update({'person_url': _site_ulr + tds[0].find('a')['href']})
                        if CUSTOM_TAG in table_object['instance'][-1]:
                            table_object['instance'][-1]['people'].append(person_info)
                else:
                    sub_institute = {CUSTOM_TAG: _bs_to_utf(tds[0]), 'people': []}
                    table_object['instance'].append(sub_institute)
            else:
                main_institute = {CUSTOM_TAG: _bs_to_utf(row), 'people': []}
                table_object['instance'].append(main_institute)

        objects['objects'].append(table_object)

    return objects


def _get_entities(table_obj):
    entities = []

    for table in table_obj['objects']:
        for _entity in table['instance']:
            entity_type = 'person'
            inst = _entity[CUSTOM_TAG]
            q_people = len(_entity['people'])
            if q_people:
                for pers in _entity['people']:

                    if POSITION in pers and 'person_name' in pers:

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
    x = _get_tables(_base_url)

    for entity in _get_entities(x):
        helpers.check(entity)
        # helpers.emit(entity)

# main scraper
if __name__ == "__main__":
    main()
