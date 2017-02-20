import unittest
import rp_main.py
import os

REPO = os.getcwd()


class RPUnitTestCase(unittest.TestCase):
    """ tests for fuctions in rp_main.py """
    def setUp(self):
        self.testdate = open(REPO).read()

    def get_recipe(self):
        """ tests different inputs and the resulting command """
        # get_recipe returns boolean when given a list of ingredients
        self.assertTrue(rp_main.get_recipe("garlic , butter, "))
        self.assertTrue(rp_main.get_recipe("     garlic , butter, "))
        self.assertTrue(rp_main.get_recipe("GaRliC ,   butter, "))
