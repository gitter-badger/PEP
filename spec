Helper Methods
You can assume the file helpers.py exists, and can import with the following statement:
import helpers
The following methods are here to help you:
fetch_string(url, [num_tries=3, encoding="utf-8", cache_hours=None])
Returns a unicode string from a web request from the given URL, with the given encoding and cache parameters, for example, the following returns a BeautifulSoup document from the Google homepage, cached for 6 hours:
import helpers

google_page = BeautifulSoup(
      helpers.fetch_string(â€œhttp://www.google.comâ€),
      cache_hours=6)
check(iterable)
Accepts a list or generator of JSON output documents, and checks the format to see if the format is acceptable, for example:
import helpers

def generate_documents():
    # ... your code here ...

check(generate_documents())
emit(document)
Prints a JSON output document in the appropriate format:
import helpers

def generate_documents():
     ... your code here ...

for doc in generate_documents():
    emit(doc)
Expected Output documents
The scraper documents are expected in JSON format with the following structure:
{
  "_meta": {
    "id": "DOC-123"               // (1)
    "entity_type": "person"       // (2)
  },
  "name": "Robert Mugabe",        // (3)
  "aka": [
    {"name": "Robert Gabriel Mugabe"},     // (4)
    {"name": "Bob Mugabe"}
  ],
  "fields": [                     // (5)
    {
      "tag": "date_of_birth",
      "value": "1924-02-21"
    },
    {
      "name": "Title",
      "value": "Dictator of Zimbabwe"
    },
    {
      "name": "Country",
      "value": "Zimbabwe"
    }
  ]
}
Notes:
1.Unique ID for the document within the scraper. This must consist of alpha-numeric and punctuation characters only, up to a maximum of 100, so they must match the following regular expression: ^[0-9a-zA-Z-_:;.]+$.
2.Entity type must be one of the following: (person, company, organisation, vessel, aircraft, unknown)
3.Name must be non-null and contain at least one letter or digit (unicode letter class).
4.AKA name must be non-null and contain at least one letter or digit (unicode letter class). If there are no AKAs, the field can be removed.
5.List of custom fields, as detailed in the next section.
Unique ID
It is important to create a good ID that is not going to likely to change between different runs of the scraper for the same page. Please follow these suggestions where possible:
1.Use any ID if given (such as news article ID, page ID etcâ€¦. if possible)
2.Use a cleaned concatenation of the name and the str.title() method, e.g. Joe BLOGGS goes to JoeBloggs.
3.If the URL is relatively clean, you can use hashlib to hash the URL and use the hexdigest() function, which will keep the ID length under 100 characters.
Fields
A field is an additional piece of information that must have at minimum the name or tag field present. The tag field indicates a special piece of information (such as the date of birth), otherwise we use the name field to denote a piece of data that we can display with the given field name.
Specially tagged fields are as follows:
url: Url for the page (usually required)
picture_url: Url for an image of a person (required if available)
country: Associated country for a person
date_of_birth: Date of birth either as year yyyy or date yyyy-mm-dd.
place_of_birth: Non-null string indicating place of birth.
date_of_death: Date of death either as year yyyy or date yyyy-mm-dd.
Please see the example for Robert Mugabe above for an example.
Notes
1.Any field value that is None or "" will be accepted and ignored.
2.Please use the given special tagged fields if possible instead of name wherever possible, so please use tag="date_of_birth" instead of name="Date of Birth" if you can.
3.tag="url" fields should be specific to the page
4.tag="country" fields should be any identifiable country text such as "UK", "GBR", "United Kingdomâ€ etc...
Checklist
Please check the following things before submitting the scraper:
1.Does it run on python 2.7 or python 3.4?
2.Have you passed the output through helpers.check?
3.Are you able to extract date of birth and / or place of birth? If so, are they tagged fields?
4.Does the scraper include all content as specified in tests in iRIS?
5.Is the code maintainable? Can another programmer easily update your code?
iRIS Platform
Iris is our platform for managing scraper content. Here is where you will be able to upload scrapers assigned to you. What to scrape and all additional info about the scraper is displayed on this platform. Before starting your scraping, you will need an account here.
In the navbar you can find the "My Jobs" section, where scrapers assigned to you reside. Pressing "Work" takes you to the scraper upload page. On this page you can also see which url is to be scraped, any notes from us, and which tests need to be passed when you upload your scraper (such as minimum number of entities required, etc ...)
For a scraper job to be marked as completed, you have to upload a script that passes all the tests specified for the scraper via the text area in the "Upload Scraper" page.
FAQs
helpers.fetch_string is giving me an error, what do I do?
This is probably due to the cache directory /var/data/scrapersCache being missing. Create the directory, or delete all contents to continue.
Is there any way I can use XPath?
You can use the lxml library (as given in requirements.txt) if you'd like to use XPath. Please find documentation here:
http://lxml.de/xpathxslt.html
One good alternative is to use BeautifulSoup CSS selectors:
http://www.crummy.com/software/BeautifulSoup/bs4/doc/#css-selectors
So the following XPath and CSS selectors are equivalent:
[XPath] //div[contains(@class,'content')]//h3
[CSS]   div.content h3
Can I use scrapy?
No, unfortunately not! We are looking to create and maintain hundreds of scrapers, and need to have them coded in a way that is maintainable and readable to as many potential programmers as possible.
For this reason, unfortunately, scrapy is disallowed.
Which data should I take?
If in doubt, take as much data as possible.