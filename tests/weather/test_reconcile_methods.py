import unittest
import pandas as pd
from reconcile_methods import counts


class ReconciliationTests(unittest.TestCase):
    def test_definitions_are_not_equivalent(self):
        result=counts(pd.Series([-2.,0.,5.,7.2,8.]))
        self.assertEqual(result,{'bounded_inclusive':3,'below_only_strict':3,'below_zero':1,'exact_upper':1})
    def test_freezing_included_only_in_below_definition(self):
        result=counts(pd.Series([-2.,-1.,0.]))
        self.assertEqual(result['below_only_strict']-result['bounded_inclusive'],2)
    def test_upper_boundary_excluded_by_strict_definition(self):
        result=counts(pd.Series([7.2]))
        self.assertEqual(result['below_only_strict'],0)
        self.assertEqual(result['bounded_inclusive'],1)


if __name__=='__main__':unittest.main()
