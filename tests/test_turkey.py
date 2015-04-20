# coding=utf-8
from collections import namedtuple
import unittest
from dev_scrapers import turkey as test_obj

test_data = {
    'page_url': 'http://www.tbmm.gov.tr/develop/owa/milletvekillerimiz_sd.liste',
    'person_name': 'Ahmet AYDIN',
    'party': 'AK Parti',
    'reg': 'BATMAN',
    'url': 'http://www.tbmm.gov.tr/develop/owa/milletvekillerimiz_sd.bilgi?p_donem=24&p_sicil=6843',
    'pos': 'Kültür Ve Turizm Bakanı'
}


def unit_test_helper(person):
    return next(_['value'] for _ in person['fields'] if _['tag'] == test_obj.x)



class TestSuite(unittest.TestCase):

    pep_url = test_obj._main_url

    def check_host(self):
        self.assertEqual(self.pep_url, test_data['page_url'])

    def setUp(self):
        obj = namedtuple('result', ['persons'])
        all_persons = test_obj.get_entities(test_obj.get_all_persons(self.pep_url))
        return obj(all_persons)

    def testName(self):
        all_names = [p['name'] for p in self.setUp().persons]
        self.assertIn(test_data['person_name'], all_names)

    def testParty(self):
        parties = []
        # for x in self.setUp().persons:
        #     party = next(_['value'] for _ in x['fields'] if _['tag'] == test_obj.POL_PRT)
        #     parties.append(party)
        unit_test_helper()

        self.assertIn(test_data['party'], set(parties))

    def testPolReg(self):
        regs = []
        for x in self.setUp().persons:
            reg = next(_['value'] for _ in x['fields'] if _['tag'] == test_obj.POL_REG)
            regs.append(reg)

        self.assertIn(test_data['reg'], set(regs))

    def testPolPos(self):
        regs = []
        for x in self.setUp().persons:
            print x
            pos = next(_['value'] for _ in x['fields'] if _['tag'] == test_obj.POL_POS)
            regs.append(pos)

        self.assertIn(test_data['pos'], set(regs))

    def runTest(self):
        pass