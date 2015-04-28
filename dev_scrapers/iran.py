# coding=utf-8
from collections import deque
import re

from utils import custom_opener, create_entity, create_id
import helpers


_host = 'http://en.parliran.ir'
MAIN_URL = '{host}/index.aspx?fkeyid=&siteid=84&pageid=3006'.format(host=_host)
PAGER = '{main}&p={index}'

PER_NAME = 'person_name'
PIC_URL = 'picture_url'
POL_REG = 'political_region'
PERSON_URL = 'url'
DATE = 'date_of_birth'
PLACE = 'place_of_birth'


def get_links():
    for num in range(1, 30):
        yield PAGER.format(main=MAIN_URL, index=num)

def get_all_persons(url):
    persons = []
    for page in get_links():
        gen = custom_opener(page)
        table = gen.find_all('div', {'style': "width:100%; float:left; clear:both;"})[1:]

        for person in table:
            image, date, place, region = (None,)*4
            person_url = _host + person.find('a').get('href')
            person_name = person.text.strip()

            sub_page = custom_opener(person_url)
            data_rows = sub_page.find('table', {'dir': 'rtl'}).find_all('tr')[1:]

            for row in data_rows:
                text_row = row.text
                if 'Date and Place of birth' in text_row:
                    date, place = text_row.strip().split(':')[-1].split('-')
                    date = {DATE: date}
                    place = {PLACE: place}
                if 'Province :' in text_row:
                    region = {POL_REG: text_row.split(':')[-1].strip()}
                    print region
                try:
                    image = {PIC_URL: _host + row.find('img')['src']}
                except Exception:
                    continue

            obj = {
                PER_NAME: person_name,
                MAIN_URL: person_url,
            }

            for el in [image, date, place, region]:
                if el:
                    obj.update(el)

            persons.append(obj)
    return persons


def get_entities(persons):
    entities = []
    for person in persons:
        name = person.pop(PER_NAME)
        values = person.values()
        unique_id = create_id([_.encode('utf-8') for _ in values])

        fields = [
            {'tag': t, 'value': v} for t, v in person.items()
        ]

        entities.append(create_entity(unique_id, 'person', name, fields))
    return entities


def main():
    main_obj = get_all_persons(MAIN_URL)

    for entity in get_entities(main_obj):
        # helpers.check(entity)
        helpers.emit(entity)


# main scraper
if __name__ == "__main__":
    main()
