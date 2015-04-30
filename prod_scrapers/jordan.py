# coding=utf-8
from dateutil import parser

def create_entity(_id, entity_type, obj_name, fields, aka=False):
    """
    easy create entity using input data

    :param _id: unique id of entity (use create_id(args))
    :param entity_type: (should be string or unicode) organisation | person etc
    :param obj_name: formal name => 'Vasya Pupkin'
    :param fields: list with {tags|names and values} => {'tag': 'political_position', 'value': 'director'}
    :param aka: list with aka names => aka = [{'name': 'Some AKA Name'}, {'name': 'Some AKA Name'}]
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
        default.update({'aka': aka})

    return default


def create_id(args):
    """
    Generate ID for entity
    :param args: strings
    :return: hashsum
    """
    from hashlib import sha224
    from re import sub

    if not isinstance(args, list):
        args = [args]
    conc_names = ''.join([_.decode('utf-8') for _ in args])
    return sha224((sub("[^a-zA-Z0-9]", "", conc_names))).hexdigest()


def custom_opener(url):
    import platform

    _OS_LINUX = True if "linux" in platform.system().lower() or 'unix' in platform.system().lower() else False
    """
    While using WINDOWS use linux=False parameter, but before final contribute change in to linux=True
    :param url: input url
    :param linux: switch between linux or windows
    """
    from bs4 import BeautifulSoup
    from helpers import fetch_string

    if _OS_LINUX:
        return BeautifulSoup(fetch_string(url, cache_hours=6))
    else:
        from urllib2 import urlopen

        try:
            return BeautifulSoup(urlopen(url, timeout=20).read())
        except Exception, e:
            print e
            pass
import helpers


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
        person = {}
        name_two, name_one, url, name = (None, )*4
        a_href = row.find('a')
        try:
            name = a_href.text
        except:
            names = row.find_all('td')
            _, name_one, _, name_two = [_.text.strip(u' \xa0*') for _ in names]

        if a_href:
            url = a_href.get('href')

        if name:
            person[PER_NAME] = name.strip(u'  \xa0*')
        if name_one:
            person[PER_NAME] = name_one
        if name_two:
            person[PER_NAME] = name_two
        if url:
            person[PERSON_URL] = url
            if 'http' not in url:
                url = _host + url
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
                                date = '{YYYY}-{MM}-{dd}'.format(YYYY=date[-1], MM=date[1], dd=date[0])
                                date = str(parser.parse(date)).split(' ')[0]

                        person[DATE] = date
        persons.append(person)
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
            # helpers.check(entity)
            helpers.emit(entity)


# main scraper
if __name__ == "__main__":
    main()
