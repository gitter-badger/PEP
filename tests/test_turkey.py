# coding=utf-8
import unittest

from dev_scrapers import turkey as test_obj
from dev_scrapers.turkey import get_entities, get_all_persons, MAIN_URL


test_data = {
    'page_url': 'http://www.tbmm.gov.tr/develop/owa/milletvekillerimiz_sd.liste',
    'person_name': 'Ahmet AYDIN',
    'party': 'AK Parti',
    'reg': 'BATMAN',
    'url': 'http://www.tbmm.gov.tr/develop/owa/milletvekillerimiz_sd.bilgi?p_donem=24&p_sicil=6843',
    # 'pos': '{}'.format('Kültür Ve Turizm Bakanı'.decode('utf-8'))
    'pos': u'Milli Savunma Komisyonu \xdcyesi\xa0Akdeniz \xdd\xe7in Birlik Parlamenter Asamblesi T\xfcrk Grubu \xdcyesi'
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
class PartyCheckTestCase(TurkeyCreateTestCase):
    def runTest(self):
        collector = []
        for person in self.persons:
            collector.append(unit_test_helper(person, test_obj.POL_PRT))
        self.assertIn(test_data['party'], set(collector))


# @unittest.skip('SomeReason')
class PoliticalRegionCheckTestCase(TurkeyCreateTestCase):
    def runTest(self):
        collector = []
        for person in self.persons:
            collector.append(unit_test_helper(person, test_obj.POL_REG))
        self.assertIn(test_data['reg'], set(collector))


# @unittest.skip('SomeReason')
class PoliticalPositionCheckTestCase(TurkeyCreateTestCase):
    def runTest(self):
        collector = []
        for person in self.persons:
            collector.append(unit_test_helper(person, test_obj.POL_POS))
        self.assertIn(test_data['pos'], set(collector))


# @unittest.skip('SomeReason')
class QuantityCheckTestCase(TurkeyCreateTestCase):
    def runTest(self):
        print len(self.persons)
        self.assertGreaterEqual(len(self.persons), 10)


def main():
    test_suite = unittest.TestSuite()
    return test_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    suite = main()
    runner.run(suite)