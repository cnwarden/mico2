
from unittest import TestCase
from db.es import ESWrapper

class TestDB(TestCase):

    def testCreate(self):
        client = ESWrapper()
        client.init_index()