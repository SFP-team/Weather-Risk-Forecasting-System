import tempfile
import unittest
import zipfile
from pathlib import Path

from place_index import build, connect, search

# geonameid, name, asciiname, alternatenames, lat, lon, class, code, country, admin1, admin2, population
PLACES = [
    (1, 'Jaíba', 'Jaiba', '', -15.338, -43.674, 'P', 'PPLA2', 'BR', '15', '3136702', 33587),
    (2, 'Jaíba', 'Jaiba', '', -15.30, -43.70, 'P', 'PPLL', 'BR', '15', '', 0),  # same town listed twice, 5 km away
    (3, 'Alma', 'Alma', '', 31.539, -82.462, 'P', 'PPLA2', 'US', 'GA', '005', 3500),
    (4, 'Alma', 'Alma', '', 48.55, -71.65, 'P', 'PPL', 'CA', '10', '', 30000),
    (5, 'Almaty', 'Almaty', 'Alma-Ata,Алматы', 43.25, 76.92, 'P', 'PPLA', 'KZ', '02', '', 2000000),
    (6, 'Almaville', 'Almaville', '', 35.9, -86.6, 'P', 'PPLH', 'US', 'TN', '', 0),  # historical place
    (7, 'Lisboa', 'Lisboa', 'Lisbon,Lisbonne', 38.72, -9.14, 'P', 'PPLC', 'PT', '14', '', 500000),
    (8, 'Alma Lake', 'Alma Lake', '', 46.0, -80.0, 'H', 'LK', 'CA', '08', '', 0),  # a lake, not a settlement
    (9, 'New York', 'New York', '', 52.6, -0.2, 'P', 'PPL', 'GB', 'ENG', '', 0),  # an English village
    (10, 'New York City', 'New York City', 'New York,NYC', 40.71, -74.01, 'P', 'PPL', 'US', 'NY', '', 8804190),
    (11, 'Jai', 'Jai', '', 34.0, 72.0, 'P', 'PPL', 'PK', '03', '', 0),
    (12, 'Jai', 'Jai', '', 34.5, 72.5, 'P', 'PPL', 'PK', '03', '', 0),  # another village 70 km away, same label
]
COUNTRIES = (('BR', 'Brazil'), ('US', 'United States'), ('CA', 'Canada'), ('KZ', 'Kazakhstan'), ('PT', 'Portugal'),
             ('GB', 'United Kingdom'), ('PK', 'Pakistan'))
ADMIN1 = (('BR.15', 'Minas Gerais'), ('US.GA', 'Georgia'), ('US.NY', 'New York'), ('CA.10', 'Quebec'),
          ('KZ.02', 'Almaty'), ('GB.ENG', 'England'), ('PK.03', 'Khyber Pakhtunkhwa'))


def geonames_fixture(directory):
    """A GeoNames-shaped dump with the PLACES rows, built into an index; returns the index path."""
    src = Path(directory) / 'dump'
    src.mkdir()
    (src / 'countryInfo.txt').write_text('#ISO\tISO3\tnum\tfips\tCountry\n' + ''.join(
        f'{cc}\tX\t0\t{cc}\t{name}\n' for cc, name in COUNTRIES), encoding='utf-8')
    (src / 'admin1CodesASCII.txt').write_text(''.join(f'{code}\t{name}\t{name}\t0\n' for code, name in ADMIN1),
                                              encoding='utf-8')
    (src / 'admin2Codes.txt').write_text('US.GA.005\tBacon County\tBacon County\t5\n', encoding='utf-8')
    rows = ['\t'.join(map(str, (gid, name, ascii_name, alts, lat, lon, fclass, code, cc, '', a1, a2, '', '', pop, '',
                                0, 'UTC', '2026-10-01')))
            for gid, name, ascii_name, alts, lat, lon, fclass, code, cc, a1, a2, pop in PLACES]
    with zipfile.ZipFile(src / 'allCountries.zip', 'w') as z:
        z.writestr('allCountries.txt', '\n'.join(rows) + '\n')
    out = Path(directory) / 'places.sqlite'
    build(src, out)
    return out


class PlaceSearchTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.db = connect(geonames_fixture(directory.name))
        self.addCleanup(self.db.close)

    def names(self, query, **kw):
        return [(r['name'], r['region']) for r in search(self.db, query, **kw)]

    def test_accents_and_case_are_ignored_and_a_double_listing_is_merged(self):
        for query in ('jaiba', 'JAÍBA', 'Jaib'):
            results = search(self.db, query)
            self.assertEqual([(r['id'], r['name'], r['region'], r['country']) for r in results],
                             [('geonames:1', 'Jaíba', 'Minas Gerais', 'Brazil')], query)

    def test_an_exact_name_beats_a_somewhat_larger_prefix_match_but_not_a_far_larger_one(self):
        self.assertEqual(self.names('alma')[0], ('Alma', 'Quebec'))  # Almaty is about 70 times larger
        self.assertEqual(self.names('alm')[0], ('Almaty', 'Almaty'))  # a prefix alone ranks by prominence
        self.assertEqual([name for name, _ in self.names('new york')], ['New York City', 'New York'])

    def test_places_the_list_could_not_tell_apart_appear_once(self):
        self.assertEqual([name for name, _ in self.names('jai')].count('Jai'), 1)

    def test_later_words_can_name_the_region_even_half_typed(self):
        self.assertEqual(self.names('alma georgia'), [('Alma', 'Georgia')])
        self.assertEqual(self.names('alma g')[0], ('Alma', 'Georgia'))
        self.assertEqual(search(self.db, 'alma bacon')[0]['county'], 'Bacon County')

    def test_alternate_names_find_the_place(self):
        self.assertEqual(self.names('Lisbon'), [('Lisboa', None)])
        self.assertEqual(self.names('Алматы'), [('Almaty', 'Almaty')])

    def test_only_current_settlements_are_searchable(self):
        self.assertEqual(self.names('almaville'), [])
        self.assertNotIn('Alma Lake', [name for name, _ in self.names('alma lake')])

    def test_queries_without_a_two_letter_word_return_nothing(self):
        self.assertEqual(self.names('a'), [])
        self.assertEqual(self.names(' ,. '), [])


if __name__ == '__main__':
    unittest.main()
