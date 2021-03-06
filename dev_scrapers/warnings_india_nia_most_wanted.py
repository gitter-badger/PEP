# coding=utf-8
from collections import deque
import hashlib
import re

from bs4 import BeautifulSoup

import helpers


_host = 'http://www.nia.gov.in'
_part_url = '{host}/wanted/'.format(host=_host)
_main_url = '{part}/wanted.aspx'.format(part=_part_url)

POL_POS = 'political_position'

POL_REG = 'political_region'
PER_NAME = 'person_name'
PIC_URL = 'picture_url'
ALIASES = 'Aliases'
WANTED_IN = 'Wanted in'
STATUS = 'Accused Status'
ADDRESS = 'Address'
CUSTOM_FIELD = 'custom_field_name'
PERSON_URL = 'url'
UNIFICATOR = '%'
wanted_fields = [WANTED_IN, STATUS, ADDRESS, ALIASES]


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


def _custom_opener(url, linux=False):
    if linux:
        return BeautifulSoup(helpers.fetch_string(url, cache_hours=6))
    else:
        from urllib2 import urlopen

        try:
            return BeautifulSoup(urlopen(url).read())
        except Exception, e:
            print e
            pass


def get_all_persons(url):
    persons = []
    main_page = _custom_opener(url, False)
    rows = main_page.find('table', {'border': '1px'}).find_all('tr')

    for row in rows:
        items = row.find_all('td')
        for item in items:
            person = {}
            image_url_part = (_.get('src').lstrip('.') for _ in item.find_all('img') if 'jpg' in _.get('src'))
            try:
                picture_url = _part_url + next(image_url_part)
            except Exception:
                picture_url = 'unsupported image type'

            link_with_name = item.find_all('a').pop()
            link_with_text = link_with_name.text
            person[PERSON_URL] = _part_url + link_with_name.get('href')

            purl = person[PERSON_URL]
            sub_page = _custom_opener(purl, linux=True)
            person[PIC_URL] = picture_url
            sub_page_trs = sub_page.find('table', {'rules': 'groups'}).find_all('tr')
            tmp_custom_field = CUSTOM_FIELD
            for tr in sub_page_trs:
                for field in wanted_fields:
                    if field in tr.text:
                        if 'Postal Address' not in tr.text:
                            # person[tmp_custom_field] = field + ': ' + ' '.join(tr.find_all('td')[-1].text.split())
                            person[field] = ' '.join(tr.find_all('td')[-1].text.split())


            if '@' in link_with_text:
                person[PER_NAME] = deque(link_with_text.split('@')).popleft()
            else:
                person[PER_NAME] = link_with_text
            persons.append(person)

    return persons


def get_entities(persons):
    entities = []
    for person in persons:
        name = person[PER_NAME]
        values = person.values()

        unique_id = _create_id([_.encode('utf-8') for _ in values])

        fields = []
        for t, v in person.items():
            if t not in wanted_fields:
                fields.append({'tag': t, 'value': v})
            else:
                fields.append({'name': t, 'value': v})

        entities.append(_create_entity(unique_id, 'person', name, fields))

    return entities


def main():
    main_obj = get_all_persons(_main_url)

    for entity in get_entities(main_obj):
        # helpers.check(entity)
        helpers.emit(entity)

# main scraper
if __name__ == "__main__":
    main()
