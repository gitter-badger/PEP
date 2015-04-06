# coding=utf-8

import hashlib
import re
import sys

from bs4 import BeautifulSoup

import helpers

_host = 'http://transparencia.tabasco.gob.mx'
_main_url = '{}/Portal/Default.aspx'.format(_host)

POL_POS = 'political_position'
PER_NAME = 'person_name'
DEP = 'department_name'
PER_URL = 'url'
PIC_URL = 'picture_url'
IMAGE = '/imagenes/top.jpg'
SPAN = 'UCtrlConsultarDependenciaDetalle_TabTitular_pnlDatosT_lblNombreTransparencia'
IMG = 'UCtrlConsultarDependenciaDetalle_TabTitular_pnlDatosT_imgFotoTransparencia'

def _custom_opener(url, linux=False):
    if linux:
        return BeautifulSoup(helpers.fetch_string(url, cache_hours=6))
    else:
        from urllib2 import urlopen
        # print url
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
    main_page = _custom_opener(url, 0)
    main_rows = [{DEP: _.text,
                  PER_URL: '{0}/Portal/{1}'.format(_host, _.get('href'))} for _ in main_page.find_all('a', {'class': 'Estilo3'})
                 if _.get('href')
                 and 'WFrmPresentarPortal.aspx?' in _.get('href')]

    for row in main_rows:
        link = row['url']
        sub_page = _custom_opener(link, 0)
        right_menu = sub_page.find('div', {'id': 'UCtrlConsultarDependenciaDetalle_TabTitular_pnlDatosT'})
        try:
            if right_menu:
                person_name = right_menu.find('span', {'id': SPAN}).text
                try:
                    person_image_url = right_menu.find('img', {'id': IMG}).get('src')
                    row.update({PER_NAME: person_name, PER_URL: person_image_url})
                except AttributeError:
                    continue
        except KeyboardInterrupt:
            # sys.exit(0)
            continue

    return _container


def get_entities(objects):
    entities = []
    for person in objects:
        person_name = person[PER_NAME]
        direct_url = person[PER_URL]
        pic_uri = person[PIC_URL]
        department = person[DEP]


        tags = [PER_NAME, PIC_URL, PER_URL, DEP]
        values = [person_name, pic_uri, direct_url, department]
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
