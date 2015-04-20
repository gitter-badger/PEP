# coding=utf-8
import unittest

from dev_scrapers import turkey as test_obj
from dev_scrapers.turkey import get_entities, get_all_persons


test_data = {
    'page_url': 'http://www.tbmm.gov.tr/develop/owa/milletvekillerimiz_sd.liste',
    'person_name': 'Ahmet AYDIN',
    'party': 'AK Parti',
    'reg': 'BATMAN',
    'url': 'http://www.tbmm.gov.tr/develop/owa/milletvekillerimiz_sd.bilgi?p_donem=24&p_sicil=6843',
    # 'pos': '{}'.format('Kültür Ve Turizm Bakanı'.decode('utf-8'))
}


def unit_test_helper(person, x):
    return next(_['value'] for _ in person['fields'] if _['tag'] == x)


def get_all_persons_for_test(url):
    return get_entities(get_all_persons(url))


class TurkeyTestSuite(unittest.TestCase):
    pep_url = test_obj._main_url
    all_persons = get_all_persons_for_test(pep_url)

    def testCheckHost(self):
        self.assertEqual(self.pep_url, test_data['page_url'])

    def testName(self):
        all_names = [p['name'] for p in self.all_persons]
        self.assertIn(test_data['person_name'], all_names)

    def testParty(self):
        all_parties = []
        for x in self.all_persons:
            all_parties.append(unit_test_helper(x, test_obj.POL_PRT))
        self.assertIn(test_data['party'], set(all_parties))

    def testPolReg(self):
        regs = []
        for x in self.all_persons:
            regs.append(unit_test_helper(x, test_obj.POL_REG))
        self.assertIn(test_data['reg'], set(regs))

    def testPolPos(self):
        positions = []
        for x in self.all_persons:
            positions.append(unit_test_helper(x, test_obj.POL_POS))
        self.assertIn(test_data['pos'], set(positions))

        # def runTest(self):
        # print 'check host test'
        #     self.testCheckHost()


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TurkeyTestSuite))
    return test_suite


runner = unittest.TextTestRunner()
runner.run(suite())
