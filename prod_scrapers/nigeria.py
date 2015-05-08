# coding=utf-8
import re

import helpers


_host = 'https://efccnigeria.org'
URLS = [
    'https://efccnigeria.org/efcc/index.php/wanted?limitstart=0',
    'https://efccnigeria.org/efcc/index.php/wanted?start=20',
    'https://efccnigeria.org/efcc/index.php/wanted?start=40'
]

PER_NAME = 'person_name'
PERSON_URL = 'url'
PIC_URL = 'picture_url'
DESCR = 'description'
WANTED_LIST = [DESCR]


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


def get_all_persons(link):
    persons = []

    page = custom_opener(link)
    data = page.find('div', {'class': 'blog'}).find_all('div', {'class': 'art-post-inner'})

    for person_link in data:
        splitter = None
        obj_url = person_link.find('a').get('href')
        obj_url = _host + obj_url if 'https://' not in obj_url else obj_url
        person_name = person_link.find('a').text.strip()

        try:
            description = custom_opener(obj_url).find('div', {'class': 'art-article'}).text.replace('\n', '').replace(
                u'\u00a0', '').replace(u'\\n', '')
            remove_text = re.search(ur'(<!--.+?-->)', description).group()
            description = description.replace(remove_text, '')
            person = {DESCR: description}

            if ' AND ' in person_name:
                splitter = 'AND'
            elif ' and ' in person_name:
                splitter = 'and'

            search_kw = 'Indian Quartet'
            if person_name == search_kw:
                namespace = [
                    {PER_NAME: 'Nemi Chand Kothari', PIC_URL: 'https://efccnigeria.org/efcc/images/NEMI-CHAND.jpg'},
                    {PER_NAME: 'Sanjay Sharma', PIC_URL: 'https://efccnigeria.org/efcc/images/SANJAY-SHARMA.jpg'},
                    {PER_NAME: 'Srinivasan Subramanian',
                     PIC_URL: 'https://efccnigeria.org/efcc/images/SRINIVASAN-SUBRAMANIA.jpg'},
                    {PER_NAME: 'Sunit Sharma', PIC_URL: 'https://efccnigeria.org/efcc/images/SUNIT-SHARMA.jpg'}
                ]

                for name in namespace:
                    name[PERSON_URL] = obj_url
                    persons.append(name)

            elif person_name != search_kw:
                if splitter:
                    new_pn = person_name.split(splitter)

                    for p_name in new_pn:
                        sub_person = {PER_NAME: p_name.strip(), PERSON_URL: obj_url.strip()}
                        working_url = sub_person[PERSON_URL]

                        body = custom_opener(working_url).find('div', {'class': 'art-article'})
                        for in_pic in [_host + pic.get('src') for pic in body.find_all('img')]:
                            for word in sub_person[PER_NAME].split():
                                if word.lower() in in_pic.lower():
                                    sub_person[PIC_URL] = in_pic

                        persons.append(sub_person)
                else:
                    person[PER_NAME] = person_name
                    person[PERSON_URL] = obj_url
                    person[PIC_URL] = _host + custom_opener(obj_url).find('div', {'class': 'art-article'}).find(
                        'img').get('src')
                    persons.append(person)

        except AttributeError:
            pass
    return persons


def get_entities(persons):
    entities = []
    for person in persons:

        name = person.pop(PER_NAME)

        values = person.values()
        try:
            unique_id = create_id([_.encode('utf-8') for _ in values])
            fields = []
            for t, v in person.items():
                if t not in WANTED_LIST:
                    fields.append({'tag': t, 'value': v})
                else:
                    fields.append({'name': t, 'value': v})

            entities.append(create_entity(unique_id, 'person', name, fields))
        except AttributeError:
            pass
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