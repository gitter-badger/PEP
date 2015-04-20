# coding=utf-8
from utils import custom_opener, create_entity, create_id
import helpers


_host = 'http://www.tbmm.gov.tr'
_main_url = '{host}/develop/owa/milletvekillerimiz_sd.liste'.format(host=_host)

POL_POS = 'political_position'
POL_REG = 'political_region'
PER_NAME = 'person_name'
PIC_URL = 'picture_url'
POL_PRT = 'political_party'
PERSON_URL = 'url'


def get_all_persons(url):
    persons = []
    main_page = custom_opener(url, linux=0)

    for row in main_page.find('table').find_all('tr'):
        person_row = row.find('a')

        if person_row:
            person_obj, _, party = row.find_all('td')
            person_name = person_obj.text
            person_prt = party.text
            person_url = person_obj.find('a').get('href')

            # sub_page = custom_opener(person_url, linux=0)
            # person_pic = sub_page.find('div', {'id': 'fotograf_alani'}).find('img').get('src')
            # pol_reg = sub_page.find('div', {'id': 'mv_ili'}).text.strip(' Milletvekili').upper()
            # pol_pos = sub_page.find('div', {'id': 'mv_gorev'}).text
            obj = {
                PER_NAME: person_name,
                PERSON_URL: person_url,
                # PIC_URL: person_pic,
                POL_PRT: person_prt,
                # POL_REG: pol_reg,
                # POL_POS: pol_pos
            }
            persons.append(obj)
    return persons


def get_entities(persons):
    entities = []
    for person in persons:
        name = person[PER_NAME]
        values = person.values()
        unique_id = create_id([_.encode('utf-8') for _ in values])

        fields = [
            {'tag': t, 'value': v} for t, v in person.items()
        ]

        entities.append(create_entity(unique_id, 'person', name, fields))

    return entities


def main():
    main_obj = get_all_persons(_main_url)

    for entity in get_entities(main_obj):
        helpers.check(entity)
        # helpers.emit(entity)


# main scraper
if __name__ == "__main__":
    main()
