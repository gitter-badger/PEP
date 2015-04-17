import hashlib
import re

from bs4 import BeautifulSoup

import helpers


_site_ulr = 'http://www.congresocam.gob.mx'
_base_url = '{}/LXI/index.php?option=com_content&view=article&id=3&Itemid=24'.format(_site_ulr)


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
    conc_names = ''.join([_.decode('utf-8') for _ in args])
    return hashlib.sha224((re.sub("[^a-zA-Z0-9]", "", conc_names))).hexdigest()


def get_rows(url):
    objects = []
    main_page = BeautifulSoup(helpers.fetch_string(url, cache_hours=6))
    rows = main_page.find('table').find_all('tr')
    for row in rows[1:]:
        name, _url = row.find_all('td')[:2]
        obj = {'name': _bs_to_utf(name),
               'picture_url': _site_ulr + _url.find('img')['src'] if _url.find('img') else _bs_to_utf(_url)}
        objects.append(obj)
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
    main_obj = get_rows(_base_url)

    for entity in get_entities(main_obj):
        # helpers.check(entity)
        helpers.emit(entity)

# main scraper
if __name__ == "__main__":
    main()
