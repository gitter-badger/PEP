# coding=utf-8
from collections import deque

from utils import custom_opener, create_entity, create_id
import helpers


_host = 'http://www.parliament.mn'
_main_url = '{host}//en/who?type=3'.format(host=_host)

POL_POS = 'political_position'
ADD_POL_POS = '!political_position'
PER_NAME = 'person_name'
PIC_URL = 'picture_url'
PERSON_URL = 'url'

TEST_DATA = '''
Rule Name	Rule Value
Scrape minimum number of entities	40
Contains given name or AKA entry, special field "name: person_name" field	Ulziisaikhan ENKHTUVSHIN
Contains a field with "tag": "url", where the value is the url of the page containing person data	http://www.parliament.mn/en/who?type=3&cid=78
Contains a field "tag": "picture_ul", with the value being the url of a picture on page	http://www.parliament.mn/en/files/images/824-7864481.jpg
Contains a field "tag": "political_position", where value is given political position	Member of the State Great Hural (Parliament) of Mongolia
Contains given name or AKA entry, special field "name: person_name" field	Zandaakhuu ENKHBOLD
Contains a field "tag": "political_position", where value is given political position	Chairman of the State Great Hural (Parliament) of Mongolia
Contains a field "tag": "picture_ul", with the value being the url of a picture on page	http://www.parliament.mn/en/files/images/658-7864481.jpg
Scrape minimum number of entities	30
Contains a field "tag": "political_position", where value is given political position	Vice Chairman of the State Great Hural (Parliament) of Mongolia
'''


def get_all_persons(url):
    persons = []
    main_page = custom_opener(url, linux=True)

    for row in main_page.find('div', {'class': 'span9'}).find_all('div', {'class': 'row'}):
        frames = row.find_all('a')

        for _row in frames:
            if _row:
                person_url = _host + _row.get('href')
                person_picture = _host + _row.find('img').get('src')
                data = deque([x.strip() for x in _row.find('div', {'class': 'cvListItem'}).text.split('\n')])
                person_name = data.popleft()
                obj = {
                    PERSON_URL: person_url,
                    PIC_URL: person_picture,
                    PER_NAME: person_name,
                    POL_POS: data.popleft()
                }

                if data:
                    obj.update({ADD_POL_POS: data.pop()})

                persons.append(obj)

    return persons


def get_entities(persons):
    entities = []
    for person in persons:
        name = person[PER_NAME]
        values = person.values()
        unique_id = create_id([_.encode('utf-8') for _ in values])

        fields = [
            {'tag': t.strip('!'), 'value': v} for t, v in person.items()
        ]

        entities.append(create_entity(unique_id, 'person', name, fields))

    return entities


def main():
    main_obj = get_all_persons(_main_url)

    for entity in get_entities(main_obj):
        # helpers.check(entity)

        helpers.emit(entity)

# main scraper
if __name__ == "__main__":
    main()
