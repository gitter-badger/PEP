import hashlib
import re

from bs4 import BeautifulSoup

import helpers


_site_ulr = 'http://www.bajacalifornia.gob.mx'
_root = '/portal/gobierno/'
_base_urls = [_.format(_site_ulr, _root) for _ in ['{0}{1}gabinete.jsp', '{0}{1}gabinete_ampliado.jsp']]


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


def get_rows(urls):
    objects = []
    # main_page = BeautifulSoup(helpers.fetch_string(urls[0], cache_hours=6))
    # other_page = BeautifulSoup(helpers.fetch_string(url[1], cache_hours=6))
    from urllib2 import urlopen

    main_page = BeautifulSoup(urlopen(urls[0]))

    other_page = BeautifulSoup(urlopen(urls[1]))

    main_rows = main_page.find_all('table', {'cellpadding': "0", 'cellspacing': "1", 'width': "100%"})


    z = []
    for row in main_rows:
        if row.find('td', {'class': 'resaltadoAzulTxt'}):
            z.append(row)


        # political_position, person_name = row[:2]
        # obj = {'political_position': _bs_to_utf(political_position),
        #        'picture_url': _bs_to_utf(person_name)}
        # objects.append(obj)
    print len(z)
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
    main_obj = get_rows(_base_urls)

    for entity in get_entities(main_obj):
        # helpers.check(entity)
        print entity
        helpers.emit(entity)

# main scraper
if __name__ == "__main__":
    main()
