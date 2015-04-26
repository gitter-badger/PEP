# coding=utf-8
import re

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


import helpers


_host = 'http://www.senate.gov.pk/'

URLS = [
    'http://www.senate.gov.pk/en/current_members.php',
    'http://www.senate.gov.pk/en/staff.php?section=5',
    'http://www.senate.gov.pk/en/staff.php?section=12'
]

START_DATE = 'active_start_date'
POL_PARTY = 'political_party'
POL_REG = 'political_region'
POL_POS = 'political_position'
PER_NAME = 'person_name'
PIC_URL = 'picture_url'
PERSON_URL = 'url'
person_re = re.compile(
    r'<strong style="font-size:30px; color:#CCCCCC;">\d{1,3}\.<\/strong><div id="borderstyle">(<table .+?</table>)')
p_re = re.compile(r'(<tr><td >\d{1,3}</td>.+?<a.+?</tr>)')


def get_all_persons(urls):
    persons = []
    from urllib2 import urlopen
    from bs4 import BeautifulSoup

    def _custom_opener_alt(_url):
        text_page = str(urlopen(_url).read()).split('\n')
        text_page = ''.join([_.strip() for _ in text_page])
        text_page = text_page.replace('<!--<hr/>-->', '')
        return text_page
    for url in urls:
        all_persons_tables = re.findall(person_re, _custom_opener_alt(url))
        if all_persons_tables:
            bs_tables = BeautifulSoup(''.join(all_persons_tables)).find_all('table')

            for person in bs_tables:
                name_block = person.find('td', {'width': '542'}).extract()
                person_url = name_block.find('a').get('href')
                name = name_block.text
                image = person.find('img').get('src')
                text_info = [_.find('td', {'width': '542'}) for _ in person.find_all('tr')]

                try:
                    pol_reg, party = text_info[2:]
                except ValueError:
                    pol_reg, party, _ = text_info[2:]

                obj = {
                    POL_PARTY: party.text,
                    POL_REG: pol_reg.text,
                    PIC_URL: _host + image,
                    PER_NAME: name.strip(),
                    PERSON_URL: _host + 'en/' + person_url
                }

                sub_page = _custom_opener_alt(obj[PERSON_URL])
                date_search = re.findall(r'Oath Taking Date</div><div class="prof_txt" >(.+?)\s</div>', sub_page)
                if date_search:
                    date = date_search.pop().split('-')
                    date = '{YYYY}-{MM}-{dd}'.format(YYYY=date[-1], MM=date[1], dd=date[0])
                    obj[START_DATE] = date

                persons.append(obj)
        else:
            all_persons_tables = re.findall(p_re, _custom_opener_alt(url))
            bs_tables = BeautifulSoup(''.join(all_persons_tables)).find_all('td')

            for td in bs_tables:
                link_name = td.find('a')

                if link_name:
                    try:
                        link_name.find('img').get('src')
                    except AttributeError:
                        obj = {}
                        name = link_name.text.strip()
                        link = _host + 'en/' + link_name.get('href')
                        obj[PER_NAME], obj[PERSON_URL] = name, link
                        sub_page = _custom_opener_alt(link)
                        position = re.findall(
                            r'<div class="staff_title" >Designation: </div><div class="staff_txt" >(.*?)</div>',
                            sub_page).pop().strip()
                        obj[POL_POS] = position
                        image = _host + re.findall(re.compile(r'<img  src="(.+?)"  style'), sub_page).pop()
                        obj[PIC_URL] = image
                        sub_data = re.findall(re.compile(r'(<div class="staff_txt" style="width:835px;" >.*?</div>)'),
                                              sub_page)
                        if sub_data:
                            soup = BeautifulSoup(sub_data[0])
                            date_regex = re.compile(r'\s(\d\w[a-z]{1,2}\s\w.+?\s\d{4}).')
                            find_date = re.findall(date_regex, soup.text)
                            if find_date:
                                from dateutil import parser

                                date_active = str(parser.parse(find_date.pop())).split(' ')[0]
                                obj[START_DATE] = date_active
                        persons.append(obj)
    return persons


def get_entities(persons):
    entities = []
    for person in persons:
        name = person.pop(PER_NAME)
        values = person.values()
        unique_id = create_id([_.encode('utf-8') for _ in values])

        fields = [
            {'tag': t, 'value': v} for t, v in person.items()
        ]

        entities.append(create_entity(unique_id, 'person', name, fields))
    return entities


def main():

    main_obj = get_all_persons(URLS)

    for entity in get_entities(main_obj):
        # helpers.check(entity)
        helpers.emit(entity)


# main scraper
if __name__ == "__main__":
    main()
