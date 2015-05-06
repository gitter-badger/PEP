# coding=utf-8
from pprint import pprint
from bs4 import BeautifulSoup
import re
from dateutil import parser

from utils import create_entity, create_id, custom_opener
import helpers

_MONTHS = {
    u' \u062d\u0632\u064a\u0631\u0627\u0646': '06'
}

_host = 'http://www.apra.gov.au'

URLS = [
    'http://www.apra.gov.au/CrossIndustry/Pages/Disqualification-Register.aspx'
]

ENTITY = 'Entity'
PER_NAME = 'person_name'
DATE = 'Date Effective'
ACT = 'Act & Section'
PRESS = 'Press Release'
DISQUALIFICATION = 'Disqualification'
PERSON_URL = 'url'

WANTED_LIST = [ENTITY, DATE, ACT, PRESS, DISQUALIFICATION]


def get_all_persons(url):
    persons = []
    page = custom_opener(url)
    rows = page.find('table', {'id': 'drTable'}).find_all('tr')

    obj_urls = (_host + row.find('a').get('href') for row in rows)

    for _url in obj_urls:

        person = {PERSON_URL: _url}

        txt_page = str(custom_opener(_url))
        table = BeautifulSoup(re.search(r'(<table border="0" cellpadding="1" cellspacing="0".+?</table>)', txt_page).group())

        nested_rows = table.find_all('tr')
        keys = ['Last Name', 'First Name', DISQUALIFICATION, DATE, ACT, ENTITY,
                PRESS]
        for nr in nested_rows:
            key, value = nr.find_all('td')
            _key, _value = key.text.strip(), value.text.strip()

            if _key == keys[0]:
                person[PER_NAME] = _value

            if _key == keys[1]:
                try:
                    person[PER_NAME] = '{f_name} {l_name}'.format(f_name=_value, l_name=person[PER_NAME])
                except UnicodeEncodeError:
                    pass

            for key in keys[2:]:
                if _key == key and _value:
                    person[key] = _value

        persons.append(person)

    return persons


def get_entities(persons):
    entities = []
    for person in persons:
        if person[PER_NAME]:
            name = person.pop(PER_NAME)

            if person[DATE]:
                person[DATE] = str(parser.parse(person[DATE])).split()[0]

            values = person.values()
            unique_id = create_id([_.encode('utf-8') for _ in values])

            fields = []
            for t, v in person.items():
                if t not in WANTED_LIST:
                    fields.append({'tag': t, 'value': v})
                else:
                    fields.append({'name': t, 'value': v})

            entities.append(create_entity(unique_id, 'person', name, fields))
    return entities


def main():
    for url in URLS:
        main_obj = get_all_persons(url)

        for entity in get_entities(main_obj):
            # helpers.check(entity)
            helpers.emit(entity)


# main scraper
if __name__ == "__main__":
    main()
