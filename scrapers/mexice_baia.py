# coding=utf-8

import hashlib
import re

from bs4 import BeautifulSoup

import helpers


_main_url = 'http://www.bajacalifornia.gob.mx/portal/gobierno/gabinete.jsp'
_second_url = 'http://www.bajacalifornia.gob.mx/portal/gobierno/gabinete_ampliado.jsp'
_tel_index = re.compile('\([0-9]{3,4}\)')

POL_POS = 'political_position'
PER_NAME = 'person_name'
DEP = 'department'


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
    # main_page = BeautifulSoup(helpers.fetch_string(urls[0], cache_hours=6))
    # other_page = BeautifulSoup(helpers.fetch_string(urls[1], cache_hours=6))
    from urllib2 import urlopen

    main_page = BeautifulSoup(urlopen(urls[0]))
    other_page = BeautifulSoup(urlopen(urls[1]))

    main_rows = main_page.find_all('table', {'cellpadding': "0", 'cellspacing': "1", 'width': "100%"})[1:]

    obje = []

    def _rec(_rows):
        for _r in _rows:
            sub_r = _r.find_all('tr')
            if sub_r:
                _rec(sub_r)
            else:
                tr_to_text = _bs_to_utf(_r)
                not_mail = '@' not in tr_to_text
                _phone = re.search(_tel_index, tr_to_text)
                if not _phone and not_mail:
                    if tr_to_text not in obje:
                        obje.append(tr_to_text)
        return obje

    objects = []
    for i in _rec(main_rows):
        if i.isupper():
            objects.append({POL_POS: i})
        else:
            objects[-1].update({PER_NAME: i})

    second_table = other_page.find_all('table', {'width': '98%', 'border': '0', 'align': 'center'})[-1]
    second_table_rows = second_table.find_all('tr')
    p = []

    for st_row in second_table_rows:
        person_container = st_row.find('span', {'class': 'linktextoResaltado'}) or st_row.find('p', {
        'class': 'linktextoResaltado'})
        header = st_row.find('td', {'class': 'subtitulos'})
        prob_name = st_row.find('span', {'class': 'textoResaltado11'})
        email_tag = st_row.find('span', {'class': 'linkrutagris'})
        if email_tag:
            email_tag.clear()

        if person_container and person_container.find('span', {'class': 'textoResaltado11'}):
            person_container.find('span', {'class': 'textoResaltado11'}).extract()

        if header:
            _header = _bs_to_utf(header)
            if 'Centro de Infraestructura y Desarrollo para las Comunidades' != _header:
                if _header:
                    p.append({DEP: _header, 'vars': []})

        elif person_container:
            pol_position = ' '.join([_.strip() for _ in _bs_to_utf(person_container).split('\n')])
            if 'rollo para las Com' not in pol_position:
                person = {POL_POS: pol_position}

                if prob_name:
                    mail_obj = prob_name.find('a')
                    x = prob_name.find('span')
                    if mail_obj and x:
                        mail_obj.clear()
                    alt_name = _bs_to_utf(prob_name)
                    if alt_name in person[POL_POS]:
                        person[POL_POS].strip()
                    person.update({PER_NAME: alt_name})
                if DEP in p[-1]:
                    p[-1]['vars'].append(person)

    for sec in p:
        dep_value = sec[DEP]
        dep_obj = {DEP: dep_value}
        for x in sec['vars']:
            x.update(dep_obj)
            objects.append(x)
    return objects


def get_entities(persons):
    entities = []
    for person in persons:
        name = person[PER_NAME]
        position = person[POL_POS]

        tags = [PER_NAME, POL_POS]
        values = [name, position.split('(')[0]]
        if DEP in person:
            deprtmt = person[DEP]
            values.append(deprtmt)
            tags.append(DEP)
        unique_id = _create_id([_.encode('utf-8') for _ in values])

        fields = [
            {'tag': t, 'value': v} for t, v in zip(tags, values)
        ]
        p_name = re.sub("^\s+", "", name.split(".")[-1].strip())
        entities.append(_create_entity(unique_id, 'person', p_name, fields))

    return entities


def main():
    main_obj = get_rows([_main_url, _second_url])

    for entity in get_entities(main_obj):
        helpers.emit(entity)

# main scraper
if __name__ == "__main__":
    main()
