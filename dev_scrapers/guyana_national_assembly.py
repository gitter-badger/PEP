# coding=utf-8
import re

from utils import custom_opener, create_entity, create_id
import helpers


_BASE_URL = "http://parliament.gov.gy/about-parliament/parliamentarian/P{page}"  # from 0 to 60 - step 10
_DOMAIN = "http://parliament.gov.gy"
WHITESPACE_PATTERN = re.compile('[\t\r\n\v]| {2,}| *$|^ *')

_EXTRA_PARTS = ['Hon.', 'Dr.', ',MP']


def get_all_persons(url):
    persons = []
    for page_index in range(0, 7):
        url = _BASE_URL.format(page=page_index * 10)
        persons += scrape_page(url)

    return persons


def scrape_page(url):
    _page = custom_opener(url)
    persons = []
    for person in _page.find_all('div', {'class': 'listing'}):
        person_url = get_url(person.find('a').get('href'))
        person_page = custom_opener(person_url)
        person_image = get_url(person.find('img').get('src'))

        obj = {
            'url': person_url,
            'picture_url': person_image
        }

        for attr in person_page.find_all('div', {'class': 'bio-content'}):
            label = attr.find('span', {'class': 'meta-title'})
            if label:
                if 'name' in label.text.lower():
                    label.extract()
                    name = WHITESPACE_PATTERN.sub('', attr.text)
                    for part in _EXTRA_PARTS:
                        name = name.replace(part, '')
                    obj['person_name'] = WHITESPACE_PATTERN.sub('', name)
                elif 'designation' in label.text.lower():
                    label.extract()
                    obj['political_position'] = WHITESPACE_PATTERN.sub('', attr.text)
                elif 'party' in label.text.lower():
                    label.extract()
                    link = attr.find('a')
                    if link:
                        link.extract()
                    obj['political_party'] = WHITESPACE_PATTERN.sub('', attr.text)
                    if obj['political_party'].endswith(' -'):
                        obj['political_party'] = obj['political_party'][:-2]

        description = person_page.find('div', {'class': 'department-description'})
        if description:
            content = ''
            for paragraph in description.find_all('p'):
                content += paragraph.text

            if content:
                obj['profile'] = content.replace(u'\u00a0', '')

        persons.append(obj)

    return persons


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
            {'tag': t, 'value': WHITESPACE_PATTERN.sub('', v)} for t, v in person.items()
        ]

        entities.append(create_entity(unique_id, 'person', name, fields))

    return entities


def main():
    main_obj = get_all_persons(_DOMAIN)

    for entity in get_entities(main_obj):
        helpers.emit(entity)
        # helpers.check(entity)

# main scraper
if __name__ == "__main__":
    main()
