# coding=utf-8

import hashlib
import re
from urlparse import parse_qs

from bs4 import BeautifulSoup

import helpers


_host = 'http://www.parliament.go.ke'
_main_url = '{host}/index.php/the-national-assembly/members'.format(host=_host)
_second_url = '{host}/index.php/the-senate/senators'.format(host=_host)

_page = 'http://www.parliament.go.ke/the-national-assembly/members?limitstart={page_counter}'

POL_POS = 'political_position'
POL_REG = 'political_region'
POL_PRT = 'political_party'
PER_NAME = 'person_name'
PIC_URL = 'picture_url'
DEP = 'department'
PERSON_URL = 'url'


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


def _custom_opener(url, linux=False):
    if linux:
        return BeautifulSoup(helpers.fetch_string(url, cache_hours=6))
    else:
        from urllib2 import urlopen

        try:
            return BeautifulSoup(urlopen(url).read())
        except:
            pass


def get_all_persons(urls):
    persons = []
    main_page = _custom_opener(urls[0])
    second_page = _custom_opener(urls[1])

    settings = {
        'first': {'link_part': '/the-national-assembly/members?start', 'page': main_page},
        'second': {'link_part': '/the-senate/senators?start', 'page': second_page}
    }

    def __pagination(element):
        last_url = element['page'].find('li', {'class': 'pagination-end'}).find('a').get('href')
        parsed_id = parse_qs(last_url)
        last_page_id = parsed_id.get(element['link_part']).pop()
        for page_count in range(0, int(last_page_id) + 10, 10):
            yield _page.format(page_counter=page_count)

    for _set in settings:
        for page in __pagination(settings[_set]):
            sub_page = _custom_opener(page)
            all_rows = sub_page.find_all('tr')[1:]
            for row in all_rows:
                bs_link = row.find('a')
                person_name = bs_link.text
                person_url = _host + bs_link.get('href')

                open_person_url = _custom_opener(person_url)

                body = open_person_url.find('div', {'class': 'itemBody'})
                person_img = body.find('img').get('src')
                p_text = body.find('p')
                person_obj = {
                    PER_NAME: person_name,
                    PERSON_URL: person_url,
                    PIC_URL: _host + person_img
                }

                for subj in str(p_text).split('<br/>'):
                    try:
                        x = {'Constituency': POL_REG, 'Party': POL_PRT, '<p>Title': POL_POS}
                        k, v = subj.split(':')
                        if k.strip() in x.keys():
                            person_obj.update({x[k.strip()]: v.strip()})
                    except ValueError:
                        continue
                persons.append(person_obj)

    return persons


def get_entities(persons):
    entities = []
    for person in persons:
        name = person[PER_NAME]
        person_url = person[PERSON_URL]
        picture_url = person[PIC_URL]
        political_region = person[POL_REG]
        political_party = person[POL_PRT]
        position = person[POL_POS]

        # tags = [PER_NAME, POL_POS]
        tags = person.keys()
        values = person.values()
        # values = [name, position.split('(')[0]]
        unique_id = _create_id([_.encode('utf-8') for _ in values])

        # fields = [
        # {'tag': t, 'value': v} for t, v in zip(tags, values)
        # ]
        # p_name = re.sub("^\s+", "", name.split(".")[-1].strip())
        entities.append(_create_entity(unique_id, 'person', name, person))

    return entities


def main():
    main_obj = get_all_persons([_main_url, _second_url])

    for entity in get_entities(main_obj):
        helpers.check(entity)
        # helpers.emit(entity)

# main scraper
if __name__ == "__main__":
    main()
