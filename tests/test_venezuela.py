# coding=utf-8
import unittest

from dev_scrapers import togo_national_assembly as test_obj
from dev_scrapers.venezuela_national_assembly import get_entities, get_all_persons, _DOMAIN


test_data = {
    'url': 'http://www.asambleanacional.gob.ve/diputado/id/66',
    'picture_url': 'http://www.asambleanacional.gob.ve/uploads/diputado/dip_1530b9cb5138e2f20ab35afe5cf7485090eede70.jpg',
    'person_name': 'ADEL EL ZABAYAR SAMARA',
    'political_party': 'Partido Socialista Unido de Venezuela',
    'political_region': u'Bolivar'
}


def unit_test_helper(person, x):
    return next(_['value'] for _ in person['fields'] if _['tag'] == x)


def get_all_persons_for_test(url):
    return get_entities(get_all_persons(url))


class VenezuelaCreateTestCase(unittest.TestCase):
    def setUp(self):
        # self.persons = persons
        self.persons = get_all_persons_for_test(_DOMAIN)

    def tearDown(self):
        self.persons = None


@unittest.skip('No such case')
class HostCheckTestCase(unittest.TestCase):
    def setUp(self):
        self.host = _DOMAIN

    def tearDown(self):
        self.host = None

    def runTest(self):
        self.assertEqual(self.host, test_data['url'])


# @unittest.skip('SomeReason')
class NameCheckTestCase(VenezuelaCreateTestCase):
    def runTest(self):
        all_names = [p['name'] for p in self.persons]
        self.assertIn(test_data['person_name'], all_names)


# @unittest.skip('SomeReason')
class PictureCheckTestCase(VenezuelaCreateTestCase):
    def runTest(self):
        collector = []
        for person in self.persons:
            collector.append(unit_test_helper(person, test_obj.PIC_URL))
        self.assertIn(test_data['picture_url'], set(collector))


@unittest.skip('No such case')
class QuantityCheckTestCase(VenezuelaCreateTestCase):
    def runTest(self):
        self.assertGreaterEqual(len(self.persons), test_data['quantity'])


# @unittest.skip('SomeReason')
class PartyCheckTestCase(VenezuelaCreateTestCase):
    def runTest(self):
        collector = []
        for person in self.persons:
            collector.append(unit_test_helper(person, test_obj.POL_PRT))
        self.assertIn(test_data['political_party'], set(collector))


def main():
    test_suite = unittest.TestSuite()
    return test_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    suite = main()
    runner.run(suite)