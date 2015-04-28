# coding=utf-8
import unittest

from dev_scrapers.guyana_national_assembly import get_entities, get_all_persons, _DOMAIN


test_data = {
    'url': 'http://parliament.gov.gy/about-parliament/parliamentarian/david-granger/',
    'url1': 'http://parliament.gov.gy/about-parliament/parliamentarian/dr-veersammy-ramayya/',
    'picture_url': 'http://parliament.gov.gy/images/member_photos/87/robert__small.jpg',
    'picture_url1': 'http://parliament.gov.gy/images/member_photos/139/ganga_persaud__small.jpg',
    'person_name': 'Robert M. Persaud',
    'person_name1': 'Ashni K. Singh',
    'political_party': 'People Progressive Party/Civic',
    'political_party1': 'Alliance for Change - AFC',
    'political_position': 'Minister of Home Affairs',
    'political_position1': 'Speaker of the House',
    'profile': 'A young Attorney at Law James Bond is a first time member of the National Assembly with opposition responsibility for Legal Affairs which includes constitution reform; public law; justice improvement; criminal justice system; legal aid and labour relations',
    'profile1': 'A Microbiologist, DrRamsammy has served in the National Assembly since 1992. The former Senior Min. of Health, Dr. Ramsammy now holds the Portfolio of Minister of Agriculture with the responsibility for Fisheries, Livestock, Other Crops, Agro-energy, Drainage and Irrigation and Forestry.',
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


class GuyanaCreateTestCase(unittest.TestCase):
    def setUp(self):
        # self.persons = persons
        self.persons = get_all_persons_for_test(_DOMAIN)

    def tearDown(self):
        self.persons = None


class UrlCheckTestCase(GuyanaCreateTestCase):
    def runTest(self):
        collector = []
        for person in self.persons:
            collector.append(unit_test_helper(person, 'url'))

        for key in ['url', 'url1']:
            self.assertIn(test_data[key], set(collector))


class NameCheckTestCase(GuyanaCreateTestCase):
    def runTest(self):
        all_names = [p['name'] for p in self.persons]
        for key in ['person_name', 'person_name1']:
            self.assertIn(test_data[key], all_names)


class PictureCheckTestCase(GuyanaCreateTestCase):
    def runTest(self):
        collector = []
        for person in self.persons:
            collector.append(unit_test_helper(person, 'picture_url'))
        for key in ['picture_url', 'picture_url1']:
            self.assertIn(test_data[key], set(collector))


class ProfileCheckTestCase(GuyanaCreateTestCase):
    def runTest(self):
        collector = []
        for person in self.persons:
            collector.append(unit_test_helper(person, 'profile', must=False))

        for key in ['profile', 'profile1']:
            self.assertIn(test_data[key], set(collector))


class PartyCheckTestCase(GuyanaCreateTestCase):
    def runTest(self):
        collector = []
        for person in self.persons:
            collector.append(unit_test_helper(person, 'political_party'))
        for key in ['political_party', 'political_party1']:
            self.assertIn(test_data[key], set(collector))


class PositionCheckTestCase(GuyanaCreateTestCase):
    def runTest(self):
        collector = []
        for person in self.persons:
            collector.append(unit_test_helper(person, 'political_position', must=False))
        for key in ['political_position', 'political_position1']:
            self.assertIn(test_data[key], set(collector))

def main():
    test_suite = unittest.TestSuite()
    return test_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    suite = main()
    runner.run(suite)