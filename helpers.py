import json
import threading
import requests
import requests.exceptions
import itertools
import sys
import time
import re
import hashlib
import tempfile
import os
import dateutil.parser
import subprocess


# cache hash
_cache_dir_path = "/var/data/scrapersCache"
_cache_cleanup_done = False
_output_lock = threading.RLock()


# cache
if not os.path.exists(_cache_dir_path):
    try:
        os.makedirs(_cache_dir_path)
    except IOError:
        _cache_dir_path = None


# version safe (python 2 or 3) convert to unicode
def _unicode(text, encoding="utf8"):
    if sys.version_info.major == 3:
        if isinstance(text, bytes):
            return text.decode(encoding, errors="ignore")
        else:
            return text
    else:
        if isinstance(text, str):
            return text.decode(encoding, errors="ignore")
        else:
            return text


# version safe (python 2 or 3) convert to bytes
def _bytes(text, encoding="utf8"):
    if sys.version_info.major == 3:
        if isinstance(text, str):
            return text.encode(encoding, errors="ignore")
        else:
            return text
    else:
        if isinstance(text, unicode):
            return text.encode(encoding, errors="ignore")
        else:
            return text


# clean a string, remove extraneous data
def _clean_string(text):

    # idiot check
    if text is None:
        return None

    # respect HTML paragraph and div tags as paragraphs to extract text
    text = _unicode(text)
    text = re.sub("[<]\\s*/?\\s*?(p|div)[^>]*[>]", "\r\n\r\n", text, flags=re.IGNORECASE)

    # split into paragraphs
    cleaned_paragraphs = []
    for para in re.split("\r\n\\s+\r\n|\n\\s+\n|\r\\s+\r", text):

        # dashes, spaces, quotes and other unicode nonsense
        para = re.sub(u"[\u00A0\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a]", " ", para, re.UNICODE)
        para = re.sub(u"[\u00AD\u2010\u2011\u2012\u2013\u2014\u2015\u2212]", "-", para, re.UNICODE)
        para = re.sub(u"[\u2018\u2019]", "\'", para, re.UNICODE)
        para = re.sub(u"[\u201c\u201d]", "\"", para, re.UNICODE)

        # escape spans and span-like tags (replace with space or no-space depending on tag)
        para = re.sub(u"[<]\\s*/?\\s*?(font|span|strong|em|b|i)[^>]*[>]", "", para, flags=re.IGNORECASE | re.UNICODE)
        para = re.sub(u"[<]\\s*/?\\s*?\\w+[^>]*[>]", " ", para, flags=re.IGNORECASE | re.UNICODE)

        # normalize spaces
        cleaned_paragraphs.append(re.sub("\\s+", " ", para).strip())

    # join paragraphs back together
    return "\r\n\r\n".join(s for s in cleaned_paragraphs if s != "")


# recursively go through a dictionary and clean / copy string
def _copy_clean(json_obj):
    if isinstance(json_obj, list):
        cleaned_source = [_copy_clean(obj) for obj in json_obj]
        return [x for x in cleaned_source if x not in ["", None]]
    elif isinstance(json_obj, dict):
        cleaned_source = [(_clean_string(key), _copy_clean(value)) for key, value in json_obj.items()]
        return {k: v for k, v in cleaned_source if v not in ["", None]}
    elif isinstance(json_obj, str):
        return _clean_string(json_obj)
    else:
        return json_obj


def _check_imported_source_json(json_original):

    # so we can change at any time, required fields indicated with a "*"
    doc_keys = [
        "_meta",
        "name",
        "aka",
        "types",
        "fields"
    ]
    meta_keys = [
        "id",
        "entity_type"
    ]
    entity_types = ["person", "organisation", "company", "vessel", "aircraft", "unknown"]
    source_types = ["sanction", "pep", "warning"]

    # check against cleaned JSON
    json_copy = _copy_clean(json_original)

    # shortcut to check the type
    def type_check(key, obj, wanted_type):
        fail_message = "{0} must be {1} (actual {2})".format(key, repr(wanted_type), repr(type(obj)))
        if wanted_type == str:
            if sys.version_info.major == 3:
                return isinstance(obj, (str, bytes))
            else:
                return isinstance(obj, (str, unicode))
        else:
            assert isinstance(obj, wanted_type), fail_message

    # check basic properties
    assert isinstance(json_copy, dict), "source document must be JSON dictionary"
    for key in json_copy.keys():
        if key not in doc_keys:
            raise AssertionError("source document has key '{0}' which is not allowed".format(key))

    # check "meta"
    if "_meta" in json_copy:
        json_meta = json_copy["_meta"]

        # check id field
        meta_id = json_meta.get("id", None)
        assert "_meta" in json_copy, "source document requires '_meta' dictionary for metadata"
        type_check("_meta.id", meta_id, str)
        assert len(meta_id) > 0, "source document '_meta.id' field is empty"
        assert re.match("^[0-9a-zA-Z-_:;.]+$", meta_id), "source document '_meta.id' field must match [0-9a-zA-Z-_:;.]"
        assert len(meta_id) < 100, "source document '_meta.id' field must be < 100 characters"

        # check "entity type" field
        meta_type = json_meta.get("entity_type", None)
        type_check("_meta.entity_type", meta_type, str)
        entity_type_fail_message = "source document '_meta.entity_type' must be one of " + ", ".join(entity_types)
        assert meta_type in entity_types, entity_type_fail_message

        # check that there are no other meta fields present
        for key in json_copy["_meta"].keys():
            if key not in meta_keys:
                raise AssertionError("source document '_meta.%s' field not permitted" % key)

    # check types
    if "types" in json_copy:
        type_check("types", json_copy["types"], list)
        for type_item in json_copy["types"]:
            if type_item not in source_types:
                raise AssertionError("type must be one of [{0}]".format(", ".join(source_types)))

    # check name field (required)
    type_check("name", json_copy.get("name", None), str)
    assert len(re.sub("\\s", "", json_copy["name"])) > 0, "source document 'name' is empty or whitespace"

    # check the AKA field is formatted properly in main document (if it exists)
    if "aka" in json_copy:
        type_check("aka", json_copy["aka"], list)
        for aka in json_copy["aka"]:
            type_check("aka (entry)", aka, dict)
            assert "name" in aka, "all 'aka' entries must have a 'name' field at the minimum"
            for key, value in aka.items():
                type_check("aka.{0} (entry)".format(key), value, str)

    # check each display field has a name or tag at minimum
    if "fields" in json_copy:
        type_check("fields", json_copy["fields"], list)
        for field in json_copy["fields"]:
            if "name" not in field and "tag" not in field:
                raise AssertionError("fields entry must have 'name' or 'tag' defined")


def _clean_cache():
    global _cache_cleanup_done
    if _cache_cleanup_done:
        return

    # don't cleanup again    
    _cache_cleanup_done = True

    # remove anything over a day old
    for file_name in os.listdir(_cache_dir_path):
        file_path = os.path.join(_cache_dir_path, file_name)
        if (time.time() - os.path.getmtime(file_path)) > 24 * 60 * 60:
            os.remove(file_path)


# run with in a cache (maybe)
def _with_cache(action, cache_key, cache_hours):

    # shortcut if not caching
    if cache_hours is None or _cache_dir_path is None:
        return action()

    # get the basics down
    hash_key = hashlib.sha224(_bytes(cache_key)).hexdigest()
    cache_path = os.path.join(_cache_dir_path, hash_key + ".download")

    # clean anything over a day old
    _clean_cache()

    # attempt to retrieve file if not too old (otherwise delete)
    if os.path.exists(cache_path):
        if (time.time() - os.path.getmtime(cache_path)) < cache_hours * 60 * 60:
            if sys.version_info.major == 3:
                with open(cache_path, "r") as cache_file:
                    return _bytes(cache_file.read(), encoding="utf8")
            else:
                with open(cache_path, "r") as cache_file:
                    return cache_file.read()
        else:
            os.remove(cache_path)

    # perform action
    result_str = action()

    # populate cache (if possible)
    try:
        if sys.version_info.major == 3:
            with open(cache_path, "w") as cache_file:
                cache_file.write(_unicode(result_str, encoding="utf8"))
        else:
            with open(cache_path, "w") as cache_file:
                cache_file.write(result_str)
    except IOError:
        pass

    # give back result
    return result_str


class FetchException(BaseException):
    """Exception on Fetch resource"""

    pass


def is_debug():
    """Returns True if we're in debug mode"""

    return "--debug" in sys.argv


def emit(source_doc):
    """Emits a source document from scraper source"""

    with _output_lock:
        if "--debug" not in sys.argv:
            print(":ACCEPT:{0}".format(json.dumps(source_doc)))
        else:
            print(json.dumps(source_doc, indent=4) + "\r\n===========")
        sys.stdout.flush()


def get_date_text(text):
    """Retrieve date text or None from random text"""

    try:
        parsed_time = dateutil.parser.parse(text)
        parsed_time = parsed_time.replace(tzinfo=None)
        return parsed_time.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return None


def fetch_string(url, num_tries=3, cache_hours=None, use_curl=True):
    """Fetch a URL as a string (returns byte string only)"""

    # non-curl downloader
    def download_with_requests():
        for tries in itertools.count(1):
            try:
                response = requests.get(url, timeout=60)
                response.raise_for_status()
                return response.content

            except requests.exceptions.HTTPError:
                exception = sys.exc_info()[1]

                # try 3 times
                if tries > num_tries:
                    code = exception.response.status_code
                    raise FetchException("Could not retrieve {0} (HTTP {1})".format(url, code))

    # attempt to download
    def download_with_curl():
        with tempfile.TemporaryFile() as temp_file:

            # write to temp file
            subprocess.call(
                ["curl",  "--retry", str(num_tries), "--silent", url],
                stdout=temp_file)

            # read from temp file
            temp_file.seek(0)
            contents = temp_file.read()

            # make sure we're understood!
            if contents:
                return contents
            else:
                raise FetchException("Could not retrieve {0}".format(url))

    # use cache to download (if appropriate)
    download = download_with_curl if use_curl else download_with_requests
    return _with_cache(download, url, cache_hours)


def check_silent(iterable):
    """Checks each document to see if it's valid, output to STDOUT

    :param iterable: an iterable of JSON documents to be checked against
    """

    # check single or multiple documents
    if isinstance(iterable, dict):
        _check_imported_source_json(iterable)
    else:
        for doc in iterable:
            _check_imported_source_json(doc)


def check(iterable):
    """Checks each document to see if it's valid, output to STDOUT.  Can be used for live testing.

    :param iterable: an iterable of JSON documents to be checked against
    """

    if isinstance(iterable, dict):

        # check a single document
        doc = iterable
        print("")
        print(json.dumps(doc, indent=4))
        print("=============================")
        _check_imported_source_json(iterable)

    else:

        # check each document
        counter = 0
        for doc in iterable:
            print("")
            print(json.dumps(doc, indent=4))
            print("=============================")
            counter += 1
            _check_imported_source_json(doc)

        # total
        print("")
        print("No problems found with {0} documents".format(counter))
