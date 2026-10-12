"""Planting window: calculated from modelled budbreak, with any published regional season beside it.

The window follows the supervisor's R workflow (southern_brazil_blueberry_climate_analogs.R): planting ends 30 days
before modelled budbreak and lasts 75 days. production.calendar() derives one window from the median budbreak. The
regional guides below are shown as a published comparison; they are resolved only from registry geography, never
inferred from a shared weather cell.
"""

METHOD = 'budbreak-planting-v1'
PUBLISHED_METHOD = 'regional-establishment-v1'
MONTHS = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
RULE_SOURCE = {'title': "Supervisor's R workflow, southern_brazil_blueberry_climate_analogs.R, planting offsets at lines "
                        "91-92 and 1219-1220. Not public.", 'url': None}
REGIONS = {
    'Citra': 'florida', 'Waldo': 'florida', 'Central Florida': 'florida', 'South Florida': 'florida',
    'Florida': 'florida', 'Georgia': 'georgia', 'Santa Catarina': 'southern_brazil',
}
GUIDANCE = {
    'florida': {
        'region': 'Florida',
        'label': 'Mid-December to mid-February',
        'start': '12-15', 'end': '02-15',
        'precision': 'Approximate mid-month guidance, not exact weather-safe dates.',
        'basis': 'UF/IFAS CIR1192 recommends mid-December to mid-February for bare-root or container-grown blueberries in Florida.',
        'conditions': ['Bare-root or container-grown nursery plants; confirm cultivar and stock suitability locally.',
                       'UF/IFAS HS1525 (2026) reports that newer UF southern highbush cultivars can produce a marketable crop within 12 months of planting.'],
        'caveat': 'The displayed window comes from home-garden guidance (UF/IFAS CIR1192, now MG359). Commercial guidance differs: UF/IFAS HS1525 (2026) advises planting in the early-spring and fall root-growth periods. Neither is a calibrated evergreen-specific planting schedule.',
        'sources': [{'title': "UF/IFAS: Blueberry Gardener's Guide (Planting and Establishment)",
                     'url': 'https://ask.ifas.ufl.edu/publication/MG359'},
                    {'title': 'UF/IFAS HS1525: Establishing New Southern Highbush Blueberry Plantings in Florida (2026)',
                     'url': 'https://journals.flvc.org/edis/article/view/140453'}],
    },
    'georgia': {
        'region': 'Georgia',
        'label': 'Winter transplanting (approximately December–February)',
        'start': '12-01', 'end': '02-28',
        'precision': 'Season only. December–February is a display convention; UGA does not specify boundary dates.',
        'basis': 'UGA Circular 946 recommends obtaining plants for winter transplanting. The displayed months represent northern meteorological winter, not a fitted or source-specified date range.',
        'conditions': ['Confirm nursery-stock dormancy, availability and planting timing with local Extension.',
                       'Remove first-season flowers or fruit; UGA also recommends removing most second-season flower buds on highbush plants.'],
        'caveat': 'Home-garden guidance covering several blueberry types. The range does not exclude suitable fall planting or establish commercial southern-highbush dates.',
        'sources': [{'title': 'UGA Extension C946: Home Garden Blueberries (Planting and Care)',
                     'url': 'https://fieldreport.caes.uga.edu/publications/C946/home-garden-blueberries/'}],
    },
    'southern_brazil': {
        'region': 'Santa Catarina, southern Brazil',
        'label': 'Winter while dormant (approximately June–August)',
        'start': '06-01', 'end': '08-31',
        'precision': 'Season only. June–August is a display convention; the source specifies winter dormancy, not dates.',
        'basis': 'The Embrapa-authored Grande potencial recommends transplanting nursery plants in winter while dormant. Southern meteorological winter provides the displayed months; observed nursery dormancy takes precedence.',
        'conditions': ['Dormant nursery plants; the source prefers two-year-old stock.',
                       'Irrigation must be available to prevent establishment losses; confirm local cultivar and nursery practice.'],
        'caveat': 'Embrapa-authored guidance hosted by Revista Cultivar (2015), not a validated Papanduva planting-date trial or an evergreen-stock schedule.',
        'sources': [{'title': 'Embrapa authors: Grande potencial (Época de plantio), Revista Cultivar',
                     'url': 'https://revistacultivar.com.br/artigos/grande-potencial'}],
    },
}
ASSUMPTIONS = ['Open-field nursery plants put in the ground before the first modelled budbreak, in a prepared, '
               'well-drained acidic root zone with irrigation available.']
LIMITATIONS = [
    "The 30- and 75-day offsets come from the supervisor's R workflow, which labels them preliminary and cites no source.",
    'The window comes from modelled budbreak, not observed dates. The app does not check frost, heat or rain inside it.',
    'No one has checked the rule against planting records. In the literature benchmark its months usually start earlier '
    'than the published planting months.',
    'Growers still need to confirm soil workability, nursery stock, cultivar, plant condition and freeze protection.',
    'This is a one-time establishment window, not annual replanting or a first-year harvest forecast.',
    'The app applies no tunnel or pot adjustment.',
]


def day_label(month_day):
    """'08-02' -> '2 Aug'."""
    month, day = map(int, month_day.split('-'))
    return f'{day} {MONTHS[month - 1]}'


def published_season(site):
    """The cited regional establishment season for a registered location, or None."""
    region = REGIONS.get(site.get('region'))
    if region is None:
        return None
    guide = GUIDANCE[region]
    return {'method': PUBLISHED_METHOD, 'region': guide['region'], 'label': guide['label'],
            'window': {'start': guide['start'], 'end': guide['end'], 'crosses_year': guide['start'] > guide['end']},
            'basis': guide['basis'], 'precision': guide['precision'], 'conditions': guide['conditions'],
            'caveat': guide['caveat'], 'sources': guide['sources']}


def planting_window(site, production=None):
    """One planting window counted back from modelled budbreak, or the reason there is none.

    `production` is the analyse() result for the location. The window exists only where the chill-triggered calendar
    applies: the rule counts back from a winter-triggered budbreak, which evergreen, tropical and too-cool locations lack.
    """
    production = production or {}
    p = production.get('assumptions') or {}
    before, length = p.get('planting_end_before_budbreak_days'), p.get('planting_window_length_days')
    base = {'method': METHOD, 'published': published_season(site), 'window': None, 'spread': None, 'budbreak': None,
            'rule': (f'Plant from {before + length} to {before} days before the typical modelled budbreak.'
                     if before else None),
            'assumptions': ASSUMPTIONS, 'limitations': LIMITATIONS, 'sources': [RULE_SOURCE]}
    calendar = production.get('calendar') or {}
    start, end, budbreak = (calendar.get(key) or {} for key in ('planting_start', 'planting_end', 'budbreak'))
    if not production or production.get('status', 'available') != 'available':
        return {**base, 'status': 'unavailable', 'label': 'Planting window unavailable', 'precision': 'Not assessed',
                'basis': None,
                'reason': ('The app calculates the planting window from the hourly crop calendar, which is unavailable '
                           'for this point.')}
    clock = production.get('chill_clock')
    if clock is not None and not clock['applicable']:
        managed = clock.get('chill_requirement_applies') is False
        return {**base, 'status': 'not_applicable', 'label': 'Set by management' if managed else 'No calculated window',
                'precision': 'Not assessed', 'basis': None,
                'reason': ' '.join([*clock['reasons'],
                                    'The planting rule counts back from a budbreak triggered by winter chill, so it gives no window here.',
                                    *(['In warm or evergreen systems the grower sets the crop cycle by management.'] if managed else [])])}
    if not before or not start.get('n'):
        return {**base, 'status': 'unavailable', 'label': 'Planting window unavailable', 'precision': 'Not assessed',
                'basis': None,
                'reason': ('This model version has no planting rule.' if not before
                           else 'No winter produced a modelled budbreak, so there is no date to count back from.')}
    window = {'start': start['median_date'], 'end': end['median_date'],
              'crosses_year': start['median_date'] > end['median_date']}
    return {**base, 'status': 'available', 'label': f"{day_label(window['start'])} to {day_label(window['end'])}",
            'window': window, 'spread': {'start': start['p10_date'], 'end': end['p90_date']},
            'budbreak': {'median': budbreak['median_date'], 'p10': budbreak['p10_date'], 'p90': budbreak['p90_date'],
                         'winters': budbreak['n']},
            'basis': (f"Typical modelled budbreak is {day_label(budbreak['median_date'])}, the median of {budbreak['n']} "
                      f'winters. Planting ends {before} days before it and lasts {length} days.'),
            'precision': (f"The window comes from modelled budbreak, not observed dates. In early winters planting can start "
                          f"on {day_label(start['p10_date'])}, and in late winters it can end on {day_label(end['p90_date'])}. "
                          'These limits use the 10th and 90th percentiles of budbreak.'),
            'reason': None}
