import itertools
import helpers
import re
from bs4 import BeautifulSoup
import urlparse
import urllib2
from pprint import pprint

_site_ulr = 'http://www.thedanishparliament.dk'
_base_url = '{}/Members/Members_in_party_groups.aspx'.format(_site_ulr)
PAGINATION = '&pageSize=100&pageNr=1'


def _create_entity():
    return {
        "_meta": {
            "id": "",
            "entity_type": ""
        },
        "name": "",
        "fields": []
    }


def _get_parties(url):
    party_objects = []
    _party_entities = []

    main_page = BeautifulSoup(urllib2.urlopen(url))

    table_party = main_page.find('table', {'class': 'telbogTable'}).find_all('tr')[1:-1]

    for row in table_party:
        party_url = _site_ulr + row.find('a')['href']
        party_id = row.find('a')['href'].split('=')[1].replace('{', '').replace('}', '')
        party_name = row.find('a').text.encode('utf8')
        party_objects.append({'party_url': party_url, 'party_id': party_id, 'party_name': party_name})
        quantity = row.find('td').text.encode('utf8')

        party_entity = _create_entity()
        party_entity['_meta']['id'] = party_id
        party_entity['_meta']['entity_type'] = 'political party'
        party_entity['name'] = party_name

        fields = [
            {'tag': 'political_party', 'value': party_name},
            {'tag': 'number_of_members', 'value': quantity}
        ]

        party_entity['fields'] = fields
        _party_entities.append(party_entity)

    return party_objects, _party_entities


parties_info, party_entities = _get_parties(_base_url)


def _get_people(party_obj):
    people_obj = []
    for party in party_obj:
        modified_url = party['party_url']+PAGINATION
        page_object = BeautifulSoup(urllib2.urlopen(modified_url))

        table_party = page_object.find('table', {'class': 'telbogTable'}).find_all('tr')[1:]
        for person in table_party:
            person_ulr = _site_ulr+person['onclick'].replace('document.location=(\'', '').replace('\')', '')
            person_id = person_ulr.split('/')[-1].strip('.aspx')
            all_td = person.find_all('td')
            person_name = ' '.join([_.text for _ in all_td[:2]])
            position = all_td[3].text
            phone = all_td[4].text.split(':')[-1].strip()
            profile_pic = _site_ulr+'/'+all_td[-1].find('img')['src']

            people_entity = _create_entity()
            people_entity['_meta']['id'] = person_id
            people_entity['_meta']['entity_type'] = 'person'
            people_entity['name'] = person_name

            fields = [{'tag': 'political_party', 'value': party['party_name']},
                      {'tag': 'url', 'value': person_ulr},
                      {'tag': 'picture_url', 'value': profile_pic},
                      {'tag': 'position', 'value': position},
                      {'tag': 'phone_number', 'value': phone}]

            open_person_url = BeautifulSoup(urllib2.urlopen(person_ulr))
            bio = open_person_url.find('div', {'class': 'tabContent clearfix'})
            first_block = bio.find('p').text
            regexp_born_in_place = re.compile('born (.+),')
            regexp_born = re.compile(r'born (.+).')

            try:
                born_string = regexp_born_in_place.search(first_block).group(0).split(',')[0].strip('born ')
            except AttributeError:
                born_string = regexp_born.search(first_block).group(0).split(',')[0].split('.')[0].strip('born ')

            if 'in' in born_string:
                date, place = born_string.split('in')
                fields.append({'tag': 'date_of_birth', 'value': date})
                fields.append({'tag': 'place_of_birth', 'value': place})
            else:
                fields.append({'tag': 'date_of_birth', 'value': born_string})

            people_entity['fields'] = fields
            pprint(people_entity)
            people_obj.append(people_entity)
    return people_obj

pprint(_get_people(parties_info))