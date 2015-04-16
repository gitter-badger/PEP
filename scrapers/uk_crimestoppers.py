import itertools
import re
import urlparse

from bs4 import BeautifulSoup

import helpers


_base_url = "https://crimestoppers-uk.org/most-wanted/?Page={0}"


def _get_scrape_urls():
    for page in itertools.count(1):
        doc = BeautifulSoup(helpers.fetch_string(_base_url.format(page), cache_hours=6))

        # find all matching tags, bail if no more
        found_urls = False
        for a in doc.find_all("a"):
            if a.has_attr("href") and "most-wanted-detail" in a["href"]:
                yield urlparse.urljoin(_base_url, a["href"])
                found_urls = True
        if not found_urls:
            break


def _tag_text(tag):
    return re.sub("\\s+|:$", " ", "".join(tag.itertext())).strip()


def _generate_entities():
    for url in _get_scrape_urls():
        doc = BeautifulSoup(helpers.fetch_string(url, cache_hours=6))

        # setup entity
        entity = {
            "_meta": {
                "id": re.sub(".*AppealId=", "", url),
                "entity_type": "person"
            },
            "types": ["warning"],
            "fields": []
        }

        # load details into fields
        for dt in doc.find("dl", class_="details").find_all("dt"):
            dd = dt.find_next_sibling("dd")
            if "suspect name" in dt.get_text().lower():
                entity["name"] = " ".join([w for w in dd.get_text().split() if re.match("^[a-zA-Z]+$", w)])
            else:
                entity["fields"].append({"name": dt.get_text().strip(), "value": dd.get_text().strip()})

        # load "full text" section
        for h3 in doc.find("div", class_="summary").find_all("h3"):
            p = h3.find_next_sibling("h3")
            if p is not None and "Full Text" in h3.get_text():
                entity["fields"].append({"name": "Summary", "value": p.get_text()})

        # give back entity
        if entity.get("name", "").strip().lower() not in ["", "unknown"]:
            yield entity


# perform full scrape
def main():
    for entity in _generate_entities():
        helpers.emit(entity)


# main scraper
if __name__ == "__main__":
    main()