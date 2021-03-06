# coding=utf-8
from utils import custom_opener, create_entity, create_id
import helpers
import re


_BASE_URL_ENG = "http://www.parliament.gov.so/index.php/en/membersparliament-3?start={index}"
_BASE_URL_SOM = 'http://www.parliament.gov.so/index.php/so/xubnaha-2?start={index}'
_DOMAIN = "http://www.parliament.gov.so"
WHITESPACE_PATTERN = re.compile('[\t\r\n\v]| {2,}| $|^ ')
_MONTHS = {
    'march': '03',
    'august': '08',
    'aug': '08'
}


def get_all_persons(arg):
    persons = []
    for index in range(0, 28):
        eng_url = _BASE_URL_ENG.format(index=str(index*10))
        persons += scrape_page(eng_url)
        som_url = _BASE_URL_SOM.format(index=str(index*10))
        persons += scrape_page(som_url)

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
        obj['picture_url'] = picture_url.replace(' ', '%20')

    date_of_election = get_date_election('p', _page, url)
    if date_of_election:
        obj["active_start_date"] = date_of_election
    else:
        date_of_election = get_date_election('div', _page, url)
        if date_of_election:
            obj["active_start_date"] = date_of_election

    return obj

def get_date_election(tag, page, url):
    html = page.prettify()
    date = re.search('(.+[Aa]ugust.+|.+[Mm]arch.+|.+[Aa]ug.+)', html)
    if date:
        content = date.group(1).lower()
        date = None

        for name in ['electionm', 'election', 'nomination']:
            if name in content:
                text = content.split(name)
                if text[-1]:
                    date = WHITESPACE_PATTERN.sub('', text[-1].replace(':', ''))

        if not date:
            date = WHITESPACE_PATTERN.sub('', content.replace(':', ''))

        date = date.split()
        if len(date) > 3:
            if date[0] == 'm':
                date.pop(0)

        month = None
        year = None
        day = None
        good_type = len(date) == 3
        for number in date:
            if number in _MONTHS:
                month = _MONTHS[number]

            elif not good_type:
                day, year = number.split(',')
            elif len(number) == 4:
                year = number
            else:
                day = number

        if month or year or day:
            return "{0}-{1}-{2}".format(year, month, day)

    return None

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
    main_obj = get_all_persons(_DOMAIN)

    for entity in get_entities(main_obj):
        # helpers.emit(entity)
        helpers.check(entity)

# main scraper
if __name__ == "__main__":
    main()
