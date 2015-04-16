import hashlib
import re

from bs4 import BeautifulSoup
from selenium import webdriver

import helpers


_base_url = "https://www.congress.gov/members?pageSize=250&page="


def role_name_splitter(text):
    return text.split(" ")


def build_document(member):
    role_and_name = role_name_splitter(member.select("h2 a")[0].get_text())
    years_served = member.select("ul.memberServed li")[0].get_text()
    party = member.select("div.memberProfile table tr")[2].select("td")[0].get_text()
    serve_state = member.select("div.memberProfile table tr")[0].select("td")[0].get_text()

    entity = {
        "_meta": {
            "id": hashlib.sha224((re.sub("[^a-zA-Z0-9]", "", role_and_name[1] + serve_state))).hexdigest(),
            "entity_type": "person"
        },
        "name": " ".join(role_and_name[1:]).strip(),
        "types": ["pep"],
        "fields": [
            {"name": "Comment", "value": "Member of US Congress"},
            {"name": "Role", "value": role_and_name[0]},
            {"name": "Years Served", "value": years_served},
            {"name": "Political Party", "value": party},
            {"name": "State", "value": serve_state}
        ]
    }
    helpers.emit(entity)


def iterate_members(html):
    for member in html.select("ul.results_list > li"):
        build_document(member)


def main():
    driver = webdriver.PhantomJS()
    driver.set_window_size(1120, 550)
    driver.implicitly_wait(10)

    for page_number in range(1, 6):
        driver.get(_base_url + str(page_number))
        bs = BeautifulSoup(driver.page_source)
        iterate_members(bs)


if __name__ == "__main__":
    main()