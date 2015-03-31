import hashlib
import re

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
    tables = main_page.find_all('table')

    for table in tables:
        table_object = {'instance': []}
        rows = table.find_all('tr')
        for row in rows:

            political_position = row.find('th', {'colspan': '2'}) or row.find('td', {'class': 'pintado'})
            person = row.find_all('td')
            person_obj_len = len(person)



            if political_position:
                table_object['instance'].append({CUSTOM_TAG: _bs_to_utf(political_position)})
            elif person_obj_len is 2:

                if len(table_object['instance']) and CUSTOM_TAG in table_object['instance'][-1]:
                    table_object['instance'][-1].update(
                        {POSITION: _bs_to_utf(person[0]), 'person_name': _bs_to_utf(person[1])})

        objects['objects'].append(table_object)
    from pprint import pprint
    pprint(objects)
    return objects


# def _get_


def _get_entities(table_obj):
    entities = []

    for table in table_obj['objects']:
        for _entity in table['instance']:
            entity_type = 'person'

            if _entity['person_name']:
                _id = _create_id(
                    [_entity[CUSTOM_TAG], _entity[POSITION], _entity['person_name']])
                fields = [{'tag': CUSTOM_TAG, 'value': _entity[CUSTOM_TAG]},
                          {'tag': POSITION, 'value': _entity[POSITION]},
                          {'tag': 'person_name', 'value': _entity['person_name']}]
                entities.append(_create_entity(_id, entity_type, _entity['person_name'], fields))

    return entities


def main():
    x = _get_tables(_base_url)

    for entity in _get_entities(x):
        helpers.check(entity)
        # helpers.emit(entity)

# main scraper
if __name__ == "__main__":
    main()
