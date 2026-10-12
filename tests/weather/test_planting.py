import unittest

import pandas as pd

from planting import planting_window
from production import calendar, empty_row, profile


def production_with_budbreak(offsets, applicable=True, chill_requirement_applies=True):
    """A minimal available v3 result whose winters broke bud `offsets` days after 1 November."""
    rows = []
    for year, budbreak in zip(range(2011, 2011 + len(offsets)), offsets):
        row = empty_row(year, 'north', pd.Timestamp(f'{year - 1}-11-01'), pd.Timestamp(f'{year}-05-01'))
        row['offset_days']['budbreak'] = budbreak
        rows.append(row)
    return {'status': 'available', 'assumptions': profile('stage_thermal_v3'),
            'calendar': calendar(rows, 'north', planting=(30, 75)),
            'chill_clock': {'applicable': applicable, 'chill_requirement_applies': chill_requirement_applies,
                            'reasons': [] if applicable else ['Only 2/15 winters produce a chill-triggered calendar.']}}


class PlantingWindowTests(unittest.TestCase):
    def test_window_counts_back_from_typical_budbreak_and_keeps_published_season(self):
        block = planting_window({'region': 'Georgia'}, production_with_budbreak([80, 90, 101]))
        self.assertEqual((block['status'], block['label']), ('available', '17 Oct to 31 Dec'))
        self.assertEqual(block['window'], {'start': '10-17', 'end': '12-31', 'crosses_year': False})
        self.assertEqual(block['budbreak']['median'], '01-30')
        self.assertEqual(block['published']['region'], 'Georgia')

    def test_window_that_spans_new_year_is_flagged(self):
        block = planting_window({}, production_with_budbreak([120] * 12))  # budbreak 1 March
        self.assertEqual(block['window'], {'start': '11-16', 'end': '01-30', 'crosses_year': True})
        self.assertIsNone(block['published'])

    def test_no_window_where_the_winter_calendar_does_not_apply(self):
        warm = planting_window({'region': 'Florida'}, production_with_budbreak([90] * 12, False, False))
        self.assertEqual((warm['status'], warm['label'], warm['window']), ('not_applicable', 'Set by management', None))
        self.assertEqual(warm['published']['region'], 'Florida')  # the published season still shows
        cool = planting_window({}, production_with_budbreak([90] * 12, False, True))
        self.assertEqual((cool['status'], cool['label']), ('not_applicable', 'No calculated window'))

    def test_unavailable_without_hourly_calendar_or_planting_rule(self):
        self.assertEqual(planting_window({}, {'status': 'unavailable'})['status'], 'unavailable')
        legacy = production_with_budbreak([90] * 12)
        legacy['assumptions'] = profile('stage_risks_v2')
        legacy.pop('chill_clock')
        self.assertIn('no planting rule', planting_window({}, legacy)['reason'])


if __name__ == '__main__':
    unittest.main()
