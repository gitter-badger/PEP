# coding=utf-8
from utils import custom_opener, create_entity, create_id
import helpers
import re


_BASE_URL = "http://www.parliament.gov.so/index.php/en/membersparliament-3?start={index}"
_DOMAIN = "http://www.parliament.gov.so"
WHITESPACE_PATTERN = re.compile('[\t\r\n\v]| {2,}| $|^ ')


def get_all_persons():
    persons = []
    for index in range(0, 22):
        url = _BASE_URL.format(index=str(index*10))
        persons += scrape_page(url)

    return persons

def scrape_page(url):
    _page = custom_opener(url)
    persons = []
    container = _page.find('tbody')
    if container:
        for person in container.find_all('a'):
            link = get_url(person.get('href'))
            persons.append(scrape_person_page(link))

    return persons

def get_picture(_page):
    container = _page.find('div', {'class': 'member-heading'}) or _page.find('tbody')
    picture_url = None
    if container:
        picture_url = container.find('img')

    for info in _page.find_all('div', {'class': 'member-bio'}):
        image = info.find('img')
        if not picture_url and image:
            picture_url = image

    if picture_url:
        return get_url(picture_url.get('src'))

    # What to do if there is no picture url at all?

def scrape_person_page(url):
    _page = custom_opener(url)

    name = WHITESPACE_PATTERN.sub('', _page.find('h2').text)
    obj = {
        'url': url,
        'person_name': name,
    }
    picture_url = get_picture(_page)
    if picture_url:
        obj['picture_url'] = picture_url

    return obj

def get_url(string):
    if not string.startswith(_DOMAIN):
        string = _DOMAIN + string

    return string


def get_entities(persons):
    entities = []
    for person in persons:
        name = person.pop('person_name')
        values = person.values()
        unique_id = create_id([_.encode('utf-8') for _ in values])

        fields = [
            {'tag': t, 'value': v} for t, v in person.items()
        ]

        entities.append(create_entity(unique_id, 'person', name, fields))

    return entities


def main():
    main_obj = get_all_persons()

    for entity in get_entities(main_obj):
        # helpers.emit(entity)
        helpers.check(entity)

# main scraper
if __name__ == "__main__":
    main()
