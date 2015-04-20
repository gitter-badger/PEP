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


def custom_opener(url):
    import platform

    _OS_LINUX = True if "linux" in platform.system().lower() or 'unix' in platform.system().lower() else False
    """
    While using WINDOWS use linux=False parameter, but before final contribute change in to linux=True
    :param url: input url
    :param linux: switch between linux or windows
    """
    from bs4 import BeautifulSoup
    from helpers import fetch_string

    if _OS_LINUX:
        return BeautifulSoup(fetch_string(url, cache_hours=6))
    else:
        from urllib2 import urlopen

        try:
            return BeautifulSoup(urlopen(url, timeout=20).read())
        except Exception, e:
            print e
            pass