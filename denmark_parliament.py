import re
from urllib import quote

from bs4 import BeautifulSoup
from dateutil import parser

import helpers


_site_ulr = 'http://www.thedanishparliament.dk'
_base_url = '{}/Members/Members_in_party_groups.aspx'.format(_site_ulr)
PAGINATION = '&pageSize=100&pageNr=1'


def _create_entity():
    return {
        "_meta": {
            "id": "",
            "entity_type": ""
        },
        "person_name": "",
        "fields": []
    }


def _get_parties(url):
    party_objects = []

    main_page = BeautifulSoup(helpers.fetch_string(url, cache_hours=6))

    table_party = main_page.find('table', {'class': 'telbogTable'}).find_all('tr')[1:-1]

    for row in table_party:
        party_url = _site_ulr + row.find('a')['href']
        party_id = row.find('a')['href'].split('=')[1].replace('{', '').replace('}', '')
        party_name = row.find('a').text.encode('utf8')
        party_objects.append({'party_url': party_url, 'party_id': party_id, 'party_name': party_name})

    return party_objects


def _get_people(party_obj):
    people_obj = []
    for party in party_obj:
        modified_url = party['party_url'] + PAGINATION
        modified_url = quote(modified_url, safe=':/?&=')

        page_object = BeautifulSoup(helpers.fetch_string(modified_url, cache_hours=6))

        table_party = page_object.find('table', {'class': 'telbogTable'}).find_all('tr')[1:]
        for person in table_party:
            person_ulr = _site_ulr + person['onclick'].replace('document.location=(\'', '').replace('\')', '')
            person_id = person_ulr.split('/')[-1].strip('.aspx')
            all_td = person.find_all('td')
            person_name = ' '.join([_.text for _ in all_td[:2]])
            position = all_td[3].text
            phone = all_td[4].text.split(':')[-1].strip()

            try:
                profile_pic = _site_ulr + '/' + all_td[-1].find('img')['src']
            except TypeError:
                profile_pic = None

            people_entity = _create_entity()
            people_entity['_meta']['id'] = person_id
            people_entity['_meta']['entity_type'] = 'person'
            people_entity['person_name'] = person_name

            fields = [{'tag': 'political_party', 'value': party['party_name']},
                      {'tag': 'url', 'value': person_ulr},
                      {'tag': 'position', 'value': position},
                      {'tag': 'phone_number', 'value': phone.strip('View biography')}]
            if profile_pic:
                fields.append({'tag': 'picture_url', 'value': profile_pic})

            open_person_url = BeautifulSoup(helpers.fetch_string(quote(person_ulr, safe=':/?&='), cache_hours=6))

            bio = open_person_url.find('div', {'class': 'tabContent clearfix'})
            first_block = bio.find('p').text
            regexp_born_in_place = re.compile('born (.+),')
            regexp_born = re.compile(r'born (.+).')

            try:
                born_string = regexp_born_in_place.search(first_block).group(0).split(',')[0].strip('born ')
            except AttributeError:
                born_string = regexp_born.search(first_block).group(0).split(',')[0].split('.')[0].strip('born ')

            if 'in' in born_string or ' at ' in born_string or ' on ' in born_string:
                try:
                    date, place = born_string.split(' in ')
                except ValueError:
                    try:
                        date, place = born_string.split(' at ')
                    except ValueError:
                        date, place = born_string.split(' on ')

                fields.append({'tag': 'date_of_birth', 'value': str(parser.parse(date)).split(' ')[0]})
                fields.append({'tag': 'place_of_birth', 'value': place})
            else:
                try:
                    fields.append({'tag': 'date_of_birth', 'value': str(parser.parse(born_string)).split(' ')[0]})
                except ValueError:
                    fields.append(
                        {'tag': 'date_of_birth', 'value': str(parser.parse(born_string.split('.')[0])).split(' ')[0]})

            people_entity['fields'] = fields
            people_obj.append(people_entity)
    return people_obj


def main():
    for entity in _get_people(_get_parties(_base_url)):
        helpers.emit(entity)

# main scraper
if __name__ == "__main__":
    main()