# coding=utf-8
from collections import deque
import re

from utils import custom_opener, create_entity, create_id
import helpers


_host = 'http://www.assemblee-nationale.tg'
MAIN_URL = '{host}/spip.php?article17'.format(host=_host)

PER_NAME = 'person_name'
PIC_URL = 'picture_url'
POL_PRT = 'political_party'
SEC_POL_PRT = '!political_party'
PERSON_URL = 'url'

_PARTY_REGEX = re.compile(ur'(\(.+?\))')


def get_all_persons(url):
    persons = []
    main_page = custom_opener(url)

    for even, odd in zip(main_page.find_all('tr', {'class': 'row_even'}),
                         main_page.find_all('tr', {'class': 'row_odd'})):
        img = even.find_all('img')
        text_info = odd.find_all('td')
        for k, v in zip(img, text_info):
            person_image = _host + '/' + k.get('src')
            name = v.text.split('(')[0].strip()
            parties = deque([_.strip('()').lstrip() for _ in re.findall(_PARTY_REGEX, v.text)])
            if not len(parties):
                parties.append('GMP')

            obj = {
                PER_NAME: name,
                PIC_URL: person_image,
                POL_PRT: parties.pop()
            }

            if len(parties):
                obj[SEC_POL_PRT] = parties.pop()
            persons.append(obj)

    return persons


def get_entities(persons):
    entities = []
    for person in persons:
        name = person.pop(PER_NAME)
        values = person.values()
        unique_id = create_id([_.encode('utf-8') for _ in values])

        fields = [
            {'tag': t.strip('!'), 'value': v} for t, v in person.items()
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
