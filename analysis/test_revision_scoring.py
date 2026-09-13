import unittest
from decimal import Decimal
from analyse_revision import marker_line_number,line_score
class MarkerLineTest(unittest.TestCase):
 def test_trailing_prose_sensitivity(self):
  self.assertEqual(marker_line_number('Work: 2+3=5\n#### 5\nExplanation: five.'),Decimal(5))
 def test_reject_words_and_units_on_answer_line(self):
  for s in ['#### 5 dollars\n5','#### Answer: 5','#### 5 or 6','Some work gives 5']:
   self.assertIsNone(marker_line_number(s))
 def test_last_declaration_and_unicode(self):
  self.assertEqual(marker_line_number('#### 6\nCorrection:\n#### ５\nDone'),Decimal(5))
 def test_bare_whole_response(self):
  self.assertEqual(marker_line_number('5'),Decimal(5));self.assertIsNone(marker_line_number('5\nDone'))
 def test_truncation_stays_missing(self):
  self.assertIsNone(line_score({'call_id':'x','reference':'5'},{'status':'success','finish_reason':'length','response_text':'#### 5'})['correct'])
if __name__=='__main__':unittest.main()
