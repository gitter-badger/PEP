import hashlib
import re
from urllib import quote
from urllib2 import urlopen

from bs4 import BeautifulSoup
from dateutil import parser

import helpers


_site_ulr = 'http://www.lapampa.gov.ar'
_base_url = '{}/autoridades-xmap.html'.format(_site_ulr)
SAFE_QUOTE = ':/?&='


def _create_entity():
    return {
        "_meta": {
            "id": "",
            "entity_type": ""
        },
        "name": "",
        "fields": []
    }


def _get_tables(url):
    objects = []
    main_page = BeautifulSoup(urlopen(url))
    tables = main_page.find_all('table')
    print tables[0]
    for table in tables:
        table_object = []
        rows = table.find_all('tr')
        for row in rows:
            # main_department = row.find('th', {'colspan': '2'})
            # sub_department = row.find('td', {'class': 'pintado'})
            political_position = row.find('th', {'colspan': '2'}) or row.find('td', {'class': 'pintado'})
            person = row.find_all('td')
            person_obj_len = len(person)

            # if main_department:
            #     table_object.append({'main_department': main_department.text})
            # elif sub_department:
            #     table_object.append({'sub_position': sub_department.text})
            if political_position:
                table_object.append({'political_position': political_position.text})
            elif person_obj_len is 2:
                table_object.append({'political_position': person[0].text})
                table_object.append({'person_name': person[1].text})
    return tables

# def _get_

def _get_people(party_obj):
    people_obj = []
    for party in party_obj:
        modified_url = party['party_url'] + PAGINATION
        modified_url = quote(modified_url, safe=SAFE_QUOTE)

        page_object = BeautifulSoup(helpers.fetch_string(modified_url, cache_hours=6))

        table_party = page_object.find('table', {'class': 'telbogTable'}).find_all('tr')[1:]
        for person in table_party:
            person_url = _site_ulr + person['onclick'].replace('document.location=(\'', '').replace('\')', '')
            person_id = person_url.split('/')[-1].strip('.aspx')
            all_td = person.find_all('td')
            person_name = ' '.join([_.text for _ in all_td[:2]])
            position = all_td[3].text
            phone = all_td[4].text.split(':')[-1].strip()

            try:
                profile_pic = _site_ulr + '/' + all_td[-1].find('img')['src']
            except TypeError:
                profile_pic = None

            people_entity = _create_entity()

            people_entity['_meta']['entity_type'] = 'person'
            people_entity['name'] = person_name
            conc_names = person_name + position + person_id
            people_entity['_meta']['id'] = hashlib.sha224((re.sub("[^a-zA-Z0-9]", "", conc_names))).hexdigest()

            fields = [{'tag': 'political_party', 'value': party['party_name']},
                      {'tag': 'url', 'value': person_url},
                      {'tag': 'position', 'value': position},
                      {'tag': 'phone_number', 'value': phone.strip('View biography')},
                      {'tag': 'country', 'value': 'Denmark'},
                      {'tag': 'person_name', 'value': person_name}]
            if profile_pic:
                fields.append(
                    {
                        'tag': 'picture_url',
                        'value': profile_pic.replace('~/media/', 'Members/~/media/').replace('84', '133').replace('x84', 'x133')
                    }
                )

            open_person_url = BeautifulSoup(helpers.fetch_string(quote(person_url, safe=SAFE_QUOTE), cache_hours=6))

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
    for entity in _get_people(_get_tables(_base_url)):
        # helpers.check(entity)
        helpers.emit(entity)

# main scraper
if __name__ == "__main__":
    main()
