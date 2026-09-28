import unittest

from benchmark import COMPARED, midpoint_month, month_gap, overlap, stage_windows, summarize, system_score


class ScoringTests(unittest.TestCase):
    def test_month_distance_wraps_the_year(self):
        self.assertEqual(month_gap(12, [1, 2]), 1)
        self.assertEqual(month_gap(6, [1, 2]), 4)
        self.assertEqual(month_gap(1, [1, 2]), 0)
        self.assertEqual(midpoint_month('11-15', '02-15'), 12)

    def test_overlap_separates_recall_and_precision(self):
        result = overlap([3, 4, 5], [4, 5, 6, 7], midpoint=4)
        self.assertEqual((result['recall'], result['precision'], result['jaccard']), (0.5, 2 / 3, 0.4))
        self.assertTrue(result['midpoint_inside'])
        miss = overlap([], [4, 5])
        self.assertEqual((miss['recall'], miss['precision'], miss['empty']), (0.0, None, True))
        self.assertIsNone(overlap([4, 5], []))

    def test_system_score_orders_classes_and_skips_unscorable(self):
        self.assertEqual(system_score('Semi-evergreen', 'mixed'), 1.0)
        self.assertEqual(system_score('Deciduous', 'semi_evergreen'), 0.5)
        self.assertEqual(system_score('Evergreen', 'deciduous'), 0.0)
        self.assertEqual(system_score('Transitional', 'mixed'), 0.5)
        self.assertEqual(system_score('Transitional', 'evergreen'), 0.5)
        self.assertIsNone(system_score(None, 'evergreen'))
        self.assertIsNone(system_score('Evergreen', 'protected_forced'))

    def test_windows_come_from_primary_scan_or_applicable_calendar_only(self):
        calendar = {k: {'median_date': v, 'n': 12} for k, v in (('flowering_start', '01-20'), ('flowering_end', '02-10'),
                                                                 ('harvest_start', '04-01'), ('harvest_end', '05-10'))}
        policy = {'min_valid_years': 12}
        not_applicable = {'risks': {'by_id': {'chill_shortfall': {'eligibility': 'not_applicable'}}, 'policy': policy},
                          'calendar': calendar}
        self.assertIsNone(stage_windows(not_applicable)['source'])
        applicable = {'risks': {'by_id': {'chill_shortfall': {'eligibility': 'ranked'}}, 'policy': policy},
                      'calendar': calendar}
        self.assertEqual(stage_windows(applicable)['harvest'], ([4, 5], 4))
        sparse = {**applicable, 'calendar': {**calendar, 'harvest_end': {'median_date': '05-10', 'n': 11}}}
        self.assertIsNone(stage_windows(sparse)['source'])
        scan = {**not_applicable, 'managed_cycle': {'role': 'primary', 'favourable': {
            'unconstrained': False, 'flowering_months': [11, 12], 'harvest_months': [2, 3, 4]}}}
        self.assertEqual(stage_windows(scan)['harvest'], ([2, 3, 4], None))

    def test_empty_managed_window_is_a_scored_miss(self):
        def site(harvest, published):
            x = {'system_score': 1.0, 'window_source': 'managed_cycle', 'unconstrained': False,
                 'windows': {'bloom': [], 'harvest': harvest}, 'bloom': None, 'r_planting_rule': None,
                 'harvest': overlap(harvest, published)}
            return {'group': 'Test', 'species': ['SHB'], 'status': 'assessed', 'profiles': dict.fromkeys(COMPARED, x)}
        summary = summarize([site([2, 3], [2, 3]), site([], [5, 6])])['Test'][COMPARED[-1]]
        self.assertEqual((summary['managed_sites'], summary['managed_empty']), (2, 1))
        self.assertEqual((summary['managed_harvest_recall'], summary['managed_harvest_precision']), (0.5, 1.0))


if __name__ == '__main__':
    unittest.main()
