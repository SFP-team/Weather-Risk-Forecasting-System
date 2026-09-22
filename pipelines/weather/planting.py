"""Cited nursery-establishment seasons, separate from a bearing plant's phenology.

The sources do not establish a global weather or budbreak-offset planting formula.
Resolve only registry geography; never infer a region from a shared weather cell.
"""

METHOD = 'regional-establishment-v1'
REGIONS = {
    'Citra': 'florida', 'Waldo': 'florida', 'Central Florida': 'florida',
    'South Florida': 'florida', 'Georgia': 'georgia', 'Santa Catarina': 'southern_brazil',
}
GUIDANCE = {
    'florida': {
        'region': 'Florida',
        'label': 'Mid-December to mid-February',
        'start': '12-15', 'end': '02-15',
        'precision': 'Approximate mid-month guidance, not exact weather-safe dates.',
        'basis': 'UF/IFAS CIR1192 recommends mid-December to mid-February for bare-root or container-grown blueberries in Florida.',
        'conditions': ['Bare-root or container-grown nursery plants; confirm cultivar and stock suitability locally.',
                       'Remove first-growing-season flowers before fruit set to favor establishment (UF/IFAS).'],
        'caveat': 'This is home-garden extension guidance, not a calibrated commercial or evergreen-specific planting schedule.',
        'sources': [{'title': "UF/IFAS: Blueberry Gardener's Guide (Planting and Establishment)",
                     'url': 'https://ask.ifas.ufl.edu/publication/MG359'}],
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


def planting_window(site):
    """Return one establishment window, or explicit absence of regional guidance."""
    region = REGIONS.get(site.get('region'))
    base = {
        'method': METHOD,
        'assumptions': ['Open-field establishment in a prepared, well-drained acidic root zone with irrigation available.'],
        'limitations': [
            'Local soil workability, nursery availability, cultivar, plant condition and freeze protection still require confirmation.',
            'This is a one-time establishment window, not annual replanting or a first-year harvest forecast.',
            'No weather optimization, budbreak subtraction, or numerical tunnel/pot adjustment is applied.',
        ],
    }
    if region is None:
        return {**base, 'status': 'unavailable', 'label': 'Regional planting window unavailable',
                'window': None, 'region': site.get('region'), 'basis': 'No regional guide has been assigned to this registered location.',
                'precision': 'Not assessed', 'sources': [],
                'reason': 'Regional planting guidance and nursery-stock context are needed. Coordinates or a shared weather cell alone do not establish them.'}
    guide = GUIDANCE[region]
    return {**base, 'status': 'available', 'label': guide['label'], 'region': guide['region'],
            'window': {'start': guide['start'], 'end': guide['end'], 'crosses_year': guide['start'] > guide['end']},
            'basis': guide['basis'], 'precision': guide['precision'],
            'assumptions': base['assumptions'] + guide['conditions'],
            'limitations': base['limitations'] + [guide['caveat']], 'sources': guide['sources'], 'reason': None}
