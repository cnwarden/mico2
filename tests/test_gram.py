
from unittest import TestCase

class TestGram(TestCase):

    def testCase1(self):
        instrument = []
        if instrument:
            print 'true'
        else:
            print 'false'
        print instrument

        p = 'SH000001,SH000002'
        a = p.split(',')
        pass

        p = 'SH000001'
        a = p.split(',')
        pass

        insts = ['1','1','1','1','1']
        print insts[:len(insts)]
