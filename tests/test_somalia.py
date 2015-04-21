# coding=utf-8
import unittest
from dev_scrapers.somalia_house_of_people import get_entities, get_all_persons, _DOMAIN


test_data = {
    'url': 'http://www.parliament.gov.so/index.php/en/xubnaha/1379-mohamed-omar-dalha-3',
    'picture_url': 'http://www.parliament.gov.so/images/profilepic.png',
    'picture_url2': 'http://www.parliament.gov.so/images/Mps_Photo/Abdiladif%20Musse%20Nor.png',
    'person_name': 'Yusuf Gelle Ugas',
    'active_start_date': '2012-08-20'
}


def unit_test_helper(person, x, must=True):
    try:
        return next(_['value'] for _ in person['fields'] if _['tag'] == x)
    except StopIteration as e:
        if must:
            raise e
        else:
            return None


def get_all_persons_for_test(url):
    return get_entities(get_all_persons(url))


class SomaliaCreateTestCase(unittest.TestCase):
    def setUp(self):
        # self.persons = persons
        self.persons = get_all_persons_for_test(_DOMAIN)

    def tearDown(self):
        self.persons = None

# @unittest.skip('SomeReason')
class NameCheckTestCase(SomaliaCreateTestCase):
    def runTest(self):
        all_names = [p['name'] for p in self.persons]
        self.assertIn(test_data['person_name'], all_names)


# @unittest.skip('SomeReason')
class PictureCheckTestCase(SomaliaCreateTestCase):
    def runTest(self):
        collector = []
        for person in self.persons:
            collector.append(unit_test_helper(person, 'picture_url'))
        self.assertIn(test_data['picture_url'], set(collector))
        self.assertIn(test_data['picture_url2'], set(collector))

# @unittest.skip('SomeReason')
class DateCheckTestCase(SomaliaCreateTestCase):
    def runTest(self):
        collector = []
        for person in self.persons:
            collector.append(unit_test_helper(person, 'active_start_date', must=False))
        self.assertIn(test_data['active_start_date'], set(collector))


def main():
    test_suite = unittest.TestSuite()
    return test_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    suite = main()
    runner.run(suite)