import itertools
import unittest
from analyse_focused_study import paired, mcnemar, holm


class PairedAnalysisTests(unittest.TestCase):
    def test_exhaustive_bounds(self):
        for states in itertools.product([None,False,True],repeat=4):
            def row(x):return {'correct':x,'prediction':str(int(x)) if x is not None else None}
            pairs=[(row(states[i]),row(states[i+1])) for i in (0,2)]
            missing=[i for i,x in enumerate(states) if x is None];values=[]
            for assignment in itertools.product([False,True],repeat=len(missing)):
                full=list(states)
                for i,x in zip(missing,assignment):full[i]=x
                values.append((int(full[1])-int(full[0])+int(full[3])-int(full[2]))/2)
            result=paired(pairs,42)
            self.assertEqual(result['difference_bound_low'],min(values))
            self.assertEqual(result['difference_bound_high'],max(values))

    def test_shared_wrong_decimal_normalization(self):
        result=paired([({'correct':False,'prediction':'12.0'},
                        {'correct':False,'prediction':'12'})],42)
        self.assertEqual(result['equal_wrong_numeric_answers'],1)
        self.assertEqual(result['neither_correct'],1)
        self.assertEqual(result['difference_b_minus_a'],0)

    def test_exact_and_holm(self):
        self.assertEqual(mcnemar(0,0),1)
        self.assertEqual(mcnemar(5,0),.0625)
        rows=[{'mcnemar_p':p} for p in [.03,.01,.04]];holm(rows)
        self.assertEqual([r['holm_p'] for r in rows],[.06,.03,.06])


if __name__=='__main__':unittest.main()
