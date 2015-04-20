# coding=utf-8
import unittest

from dev_scrapers import togo_national_assembly as test_obj
from dev_scrapers.togo_national_assembly import get_entities, get_all_persons, MAIN_URL


test_data = {
    'person_name': 'ADZIMA Kossi Mensa',
    'party': 'CAR',
    'pic': 'http://www.assemblee-nationale.tg/IMG/jpg/YABRE.jpg',
    'quantity': 70,
    'page_url': 'http://www.assemblee-nationale.tg/spip.php?article17'
}


def unit_test_helper(person, x):
    return next(_['value'] for _ in person['fields'] if _['tag'] == x)


def get_all_persons_for_test(url):
    return get_entities(get_all_persons(url))


class TurkeyCreateTestCase(unittest.TestCase):
    def setUp(self):
        # self.persons = persons
        self.persons = get_all_persons_for_test(MAIN_URL)

    def tearDown(self):
        self.persons = None


class HostCheckTestCase(unittest.TestCase):
    def setUp(self):
        self.host = MAIN_URL

    def tearDown(self):
        self.host = None

    def runTest(self):
        self.assertEqual(self.host, test_data['page_url'])


# @unittest.skip('SomeReason')
class NameCheckTestCase(TurkeyCreateTestCase):
    def runTest(self):
        all_names = [p['name'] for p in self.persons]
        self.assertIn(test_data['person_name'], all_names)


# @unittest.skip('SomeReason')
class PictureCheckTestCase(TurkeyCreateTestCase):
    def runTest(self):
        collector = []
        for person in self.persons:
            collector.append(unit_test_helper(person, test_obj.PIC_URL))
        self.assertIn(test_data['pic'], set(collector))


# @unittest.skip('SomeReason')
class QuantityCheckTestCase(TurkeyCreateTestCase):
    def runTest(self):
        self.assertGreaterEqual(len(self.persons), test_data['quantity'])


# @unittest.skip('SomeReason')
class PartyCheckTestCase(TurkeyCreateTestCase):
    def runTest(self):
        collector = []
        for person in self.persons:
            collector.append(unit_test_helper(person, test_obj.POL_PRT))
        self.assertIn(test_data['party'], set(collector))


def main():
    test_suite = unittest.TestSuite()
    return test_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    suite = main()
    runner.run(suite)