# coding=utf-8
from dateutil import parser

from utils import create_entity, create_id, custom_opener
import helpers

_MONTHS = {
    u' \u062d\u0632\u064a\u0631\u0627\u0646': '06'
}

_host = 'http://www.senate.jo'

URLS = [
    'http://www.senate.jo/content/%D8%A3%D8%B9%D8%B6%D8%A7%D8%A1-%D8%A7%D9%84%D9%85%D8%AC%D9%84%D8%B3-%D8%A7%D9%84%D8%AD%D8%A7%D9%84%D9%8A'
]

START_DATE = 'active_start_date'
POL_PARTY = 'political_party'
POL_REG = 'political_region'
POL_POS = 'political_position'
ALI = 'Aliases'
PER_NAME = 'person_name'
PLACE_BIRTH = 'place_of_birth'
DATE = 'date_of_birth'
PIC_URL = 'picture_url'
PERSON_URL = 'url'

WANTED_LIST = [ALI]


def get_all_persons(url):
    persons = []
    page = custom_opener(url)
    rows = page.find('table', {'dir': 'rtl'}).find_all('tr')

    for row in rows:
        name_two, name_one, url, name = (None, ) * 4
        for a_href in row.find_all('a'):
            person = {}
            try:
                name = a_href.text
                if a_href:
                    url = a_href.get('href')
                person[PER_NAME] = name

                if url:

                    if 'http' not in url:
                        url = _host + url

                    person[PERSON_URL] = url
                    sub_page = custom_opener(url)
                    person[PIC_URL] = _host + sub_page.find('div', {'class': 'senator-image'}).find('img').get('src')
                    table = sub_page.find('table', {'class': 'senator-profile-table'})
                    for _row in table.find_all('tr'):
                        label = _row.find('h3', {'class': 'field-label'})
                        if label:
                            if label and u'إسم الشهرة:' in label:
                                person[ALI] = _row.find('div', {'class': 'field-item'}).text.strip()
                            if label and u'مكان الولادة:' in label:
                                person[PLACE_BIRTH] = _row.find('div', {'class': 'field-item'}).text.strip()

                            if label and u'تاريخ الميلاد:' in label:
                                date = _row.find('div', {'class': 'field-item'}).text.strip().strip('.')
                                separators = ['/']
                                for sep in separators:
                                    if sep in date:
                                        date = date.split(sep)

                                        if date[1] in _MONTHS.keys():
                                            date[1] = _MONTHS[date[1]]
                                        date = '{YYYY}-{MM}-{dd}'.format(YYYY=date[-1], MM=date[1], dd=date[0])
                                        date = str(parser.parse(date)).split(' ')[0]

                                person[DATE] = date
                    persons.append(person)
            except:
                continue

    return persons


def get_entities(persons):
    entities = []
    for person in persons:
        name = person.pop(PER_NAME)
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
            helpers.check(entity)
            # helpers.emit(entity)


# main scraper
if __name__ == "__main__":
    main()
