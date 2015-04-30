# coding=utf-8
import unittest

from dev_scrapers import jordan as test_obj
from dev_scrapers.jordan import get_entities, get_all_persons


test_data = {
    'person_name': u'منير صوبر',
    'url': 'http://www.senate.jo/content/%D8%B3%D8%B9%D8%A7%D8%AF%D8%A9-%D8%A7%D9%84%D8%AF%D9%83%D8%AA%D9%88%D8%B1-%D9%85%D8%AD%D9%85%D8%AF-%D8%A7%D8%A8%D8%B1%D8%A7%D9%87%D9%8A%D9%85-%D8%B9%D8%A8%D9%8A%D8%AF%D8%A7%D8%AA',
    'pic': 'http://www.senate.jo/sites/default/files/images/yassin_alhusban.senator.jpg',
    'date': '1939-02-13',
    'place': u'الصريح – اربد'
}


def unit_test_helper(person, x):
    return next(_['value'] for _ in person['fields'] if _['tag'] == x)


def get_all_persons_for_test(url):
    return get_entities(get_all_persons(url))


class TurkeyCreateTestCase(unittest.TestCase):
    def setUp(self):
        # self.persons = persons
        self.persons = get_all_persons_for_test('http://www.senate.jo/content/%D8%A3%D8%B9%D8%B6%D8%A7%D8%A1-%D8%A7%D9%84%D9%85%D8%AC%D9%84%D8%B3-%D8%A7%D9%84%D8%AD%D8%A7%D9%84%D9%8A')

    def tearDown(self):
        self.persons = None


# @unittest.skip('SomeReason')
class NameCheckTestCase(TurkeyCreateTestCase):
    def runTest(self):
        all_names = [p['name'] for p in self.persons]
        self.assertIn(test_data['person_name'], all_names)


def main():
    test_suite = unittest.TestSuite()
    return test_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    suite = main()
    runner.run(suite)