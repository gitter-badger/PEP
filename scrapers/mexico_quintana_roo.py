# coding=utf-8

import hashlib
import re

from bs4 import BeautifulSoup

import helpers


_host = 'http://transparencia.qroo.gob.mx'
_main_url = '{}/portal/Transparencia/BusquedaDirectorioServidor.php'.format(_host)

POL_POS = 'political_position'
PER_NAME = 'person_name'
ADD_NAME = 'additional_name'
DEP = 'department_name'
PER_URL = 'url'
PIC_URL = 'picture_url'
IMAGE = '/imagenes/top.jpg'
SPAN = 'UCtrlConsultarDependenciaDetalle_TabTitular_pnlDatosT_lblNombreTransparencia'
SPAN_2 = 'UCtrlConsultarDependenciaDetalle_PestanaDetalles_pnlDatos_lblResponsableSolicitud'
IMG = 'UCtrlConsultarDependenciaDetalle_TabTitular_pnlDatosT_imgFotoTransparencia'
IMG_2 = 'UCtrlConsultarDependenciaDetalle_PestanaDetalles_pnlDatos_Foto'


def _custom_opener(url, linux=False):
    if linux:
        return BeautifulSoup(helpers.fetch_string(url, cache_hours=6))
    else:
        from urllib2 import urlopen

        return BeautifulSoup(urlopen(url).read())


def _create_entity(_id, entity_type, obj_name, fields, aka=False):
    """
    easy create entity using input data

    :param _id: unique id of entity
    :param entity_type: organisation | person etc
    :param obj_name: formal name
    :param fields: list with {tags and values}
    :return: dict
    """
    default = {
        "_meta": {
            "id": _id,
            "entity_type": entity_type
        },
        "name": obj_name,
        "fields": fields
    }

    if aka:
        # {'aka': 'name': '??'}
        default.update({'aka': [aka]})
    return default


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
    container = []
    main_page = _custom_opener(url, linux=True)

    main_table_rows = main_page.find('table', {'width': '100%', 'border': '0', 'cellspacing': '2'}).find_all('tr')[1:]
    # print len(main_table_rows)
    c = 0
    for row in main_table_rows:
        data = row.find_all('td')[:2]
        person_name, other_info = data
        pol_pos = _bs_to_utf(other_info.find('strong').extract())
        administration = _bs_to_utf(other_info)
        obj = {PER_NAME: _bs_to_utf(person_name), POL_POS: pol_pos, DEP: administration}
        container.append(obj)

    return container


def get_entities(objects):
    entities = []
    for person in objects:
        print person
        person_name = person[PER_NAME]
        department = person[DEP]
        pol_pos = person[POL_POS]

        # person_name = re.sub("^\s+", "", person_name.split(".")[-1].strip())
        tags = [PER_NAME, DEP, POL_POS]
        values = [person_name, department, pol_pos]

        unique_id = _create_id([_.encode('utf-8') for _ in values])

        fields = [
            {'tag': t, 'value': v} for t, v in zip(tags, values)
        ]

        entity = _create_entity(unique_id, 'person', person_name, fields)
        entities.append(entity)

    return entities


def main():
    main_obj = get_rows(_main_url)
    for entity in get_entities(main_obj):
        # helpers.check(entity)
        helpers.emit(entity)

# main scraper
if __name__ == "__main__":
    main()
