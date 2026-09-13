import unittest
from decimal import Decimal
from focused_scoring import final_number, score_record


class FrozenScorerTests(unittest.TestCase):
    def test_explicit_or_bare(self):
        for text in ['12','#### 12','Calculation 3 * 4 = 12\n#### 12','#### １２','#### ١٢']:
            self.assertEqual(final_number(text),Decimal(12))
        self.assertEqual(final_number('#### 1,200.50'),Decimal('1200.5'))
        self.assertEqual(final_number('#### -2'),Decimal(-2))

    def test_no_incidental_numbers(self):
        for text in ['The answer is 12.','#### 3+9=12','#### 12 apples','#### 1/2',
                     '#### 1,20','There are 12 items and 3 are left','#### 12\nExplanation: 3*4',None]:
            self.assertIsNone(final_number(text))

    def test_failure_and_truncation_never_become_wrong(self):
        call={'call_id':'a','reference':'12'}
        for record in [None,{'status':'error'},
                       {'status':'success','finish_reason':'length','response_text':'#### 12'},
                       {'status':'success','finish_reason':'eos','response_text':'12 apples'}]:
            self.assertIsNone(score_record(call,record)['correct'])
        for text,expected in [('#### 12',True),('#### 13',False)]:
            self.assertIs(score_record(call,{'status':'success','finish_reason':'eos',
                                             'response_text':text})['correct'],expected)


if __name__=='__main__':unittest.main()
