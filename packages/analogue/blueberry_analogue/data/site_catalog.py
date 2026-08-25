"""Commercial blueberry truth set: production-district coordinates.

Points are town or named-operation centroids, not block corners.
Precision is district, not a 20 ha plant decision.
System is labeled where public practice is consistent; otherwise unknown.
"""

from __future__ import annotations

from typing import Any

# Columns match truth_set.csv
# outcome: commercial_success | commercial_caution | known_failure | horticultural_absence
# geocode_precision: town | district | farm

SITES: list[dict[str, Any]] = []


def _s(
    site_id: str,
    name: str,
    country: str,
    region: str,
    admin: str,
    lat: float,
    lon: float,
    cultivar_class: str,
    cultivar: str,
    media: str,
    structure: str,
    cover: str,
    habit: str,
    outcome: str,
    source: str,
    notes: str = "",
    geocode_precision: str = "town",
) -> dict[str, Any]:
    return {
        "site_id": site_id,
        "name": name,
        "country": country,
        "region": region,
        "admin": admin,
        "lat": lat,
        "lon": lon,
        "cultivar_class": cultivar_class,
        "cultivar": cultivar,
        "media": media,
        "structure": structure,
        "cover": cover,
        "habit": habit,
        "outcome": outcome,
        "source": source,
        "geocode_precision": geocode_precision,
        "notes": notes,
    }


def _add(rows: list[dict[str, Any]]) -> None:
    SITES.extend(rows)


# --- Florida SHB / evergreen ---
_add(
    [
        _s("us-fl-alachua", "Alachua / Windsor belt", "US", "US-SE", "Florida", 29.65, -82.33, "low_chill_shb", "emerald", "pine_bark", "open", "none", "deciduous", "commercial_success", "UF/IFAS + NASS blueberry counties", "North-central deciduous core."),
        _s("us-fl-waldo", "Waldo", "US", "US-SE", "Florida", 29.79, -82.17, "low_chill_shb", "emerald", "pine_bark", "open", "none", "deciduous", "commercial_success", "UF/IFAS production belt"),
        _s("us-fl-hawthorne", "Hawthorne", "US", "US-SE", "Florida", 29.59, -82.08, "low_chill_shb", "jewel", "pine_bark", "open", "none", "deciduous", "commercial_success", "UF/IFAS production belt"),
        _s("us-fl-melrose", "Melrose", "US", "US-SE", "Florida", 29.71, -82.05, "low_chill_shb", "emerald", "pine_bark", "open", "none", "deciduous", "commercial_success", "UF/IFAS production belt"),
        _s("us-fl-earleton", "Earleton", "US", "US-SE", "Florida", 29.72, -82.10, "low_chill_shb", "emerald", "pine_bark", "open", "none", "deciduous", "commercial_success", "UF/IFAS production belt"),
        _s("us-fl-interlachen", "Interlachen", "US", "US-SE", "Florida", 29.62, -81.89, "low_chill_shb", "jewel", "pine_bark", "open", "none", "deciduous", "commercial_success", "Putnam County"),
        _s("us-fl-palatka", "Palatka / Putnam Hall", "US", "US-SE", "Florida", 29.65, -81.66, "low_chill_shb", "emerald", "pine_bark", "open", "none", "deciduous", "commercial_success", "FAWN Putnam Hall"),
        _s("us-fl-citra", "Citra PSREU", "US", "US-SE", "Florida", 29.41, -82.17, "low_chill_shb", "emerald", "pine_bark", "open", "none", "deciduous", "commercial_success", "UF PSREU", "Research plus commercial belt.", "farm"),
        _s("us-fl-ocala", "Ocala north", "US", "US-SE", "Florida", 29.19, -82.14, "high_chill_shb", "star", "pine_bark", "open", "none", "deciduous", "commercial_success", "UF Star range"),
        _s("us-fl-south-ocala", "South of Ocala", "US", "US-SE", "Florida", 28.95, -82.12, "high_chill_shb", "star", "pine_bark", "open", "none", "deciduous", "known_failure", "UF: Star fails south of Ocala"),
        _s("us-fl-floral-city", "Floral City", "US", "US-SE", "Florida", 28.75, -82.30, "low_chill_shb", "snowchaser", "pine_bark", "open", "none", "deciduous", "commercial_caution", "Citrus County early SHB", "Freeze magnet."),
        _s("us-fl-brooksville", "Brooksville", "US", "US-SE", "Florida", 28.56, -82.39, "evergreen_zero_chill", "snowchaser_evergreen", "pine_bark", "open", "none", "evergreen", "commercial_success", "Hernando evergreen"),
        _s("us-fl-plant-city", "Plant City", "US", "US-SE", "Florida", 28.02, -82.11, "evergreen_zero_chill", "avanti", "pine_bark", "open", "none", "evergreen", "commercial_success", "Hillsborough"),
        _s("us-fl-polk", "Polk / Lake Alfred", "US", "US-SE", "Florida", 28.09, -81.73, "evergreen_zero_chill", "avanti", "pine_bark", "open", "none", "evergreen", "commercial_success", "CREC / FAWN Lake Alfred"),
        _s("us-fl-haines-city", "Haines City", "US", "US-SE", "Florida", 28.11, -81.62, "evergreen_zero_chill", "kestrel", "pine_bark", "open", "none", "evergreen", "commercial_success", "Polk"),
        _s("us-fl-lake-wales", "Lake Wales", "US", "US-SE", "Florida", 27.90, -81.59, "evergreen_zero_chill", "avanti", "pine_bark", "open", "none", "evergreen", "commercial_success", "Polk"),
        _s("us-fl-sebring", "Sebring / Highlands", "US", "US-SE", "Florida", 27.50, -81.44, "evergreen_zero_chill", "snowchaser_evergreen", "pine_bark", "open", "none", "evergreen", "commercial_success", "FAWN Sebring"),
        _s("us-fl-lake-placid", "Lake Placid", "US", "US-SE", "Florida", 27.29, -81.36, "evergreen_zero_chill", "kestrel", "pine_bark", "open", "none", "evergreen", "commercial_success", "Highlands"),
        _s("us-fl-wauchula", "Wauchula", "US", "US-SE", "Florida", 27.55, -81.81, "evergreen_zero_chill", "avanti", "pine_bark", "open", "none", "evergreen", "commercial_success", "Hardee"),
        _s("us-fl-avon-park", "Avon Park", "US", "US-SE", "Florida", 27.60, -81.51, "evergreen_zero_chill", "snowchaser_evergreen", "pine_bark", "open", "none", "evergreen", "commercial_success", "Highlands"),
        _s("us-fl-clermont", "Clermont", "US", "US-SE", "Florida", 28.55, -81.76, "low_chill_shb", "snowchaser", "pine_bark", "open", "none", "deciduous", "commercial_caution", "Lake County", "Early bloom freeze."),
        _s("us-fl-umatilla", "Umatilla", "US", "US-SE", "Florida", 28.93, -81.67, "low_chill_shb", "emerald", "pine_bark", "open", "none", "deciduous", "commercial_success", "Lake/Marion edge"),
        _s("us-fl-pierson", "Pierson", "US", "US-SE", "Florida", 29.24, -81.46, "low_chill_shb", "emerald", "pine_bark", "open", "none", "deciduous", "commercial_success", "Volusia"),
        _s("us-fl-hastings", "Hastings", "US", "US-SE", "Florida", 29.72, -81.51, "low_chill_shb", "star", "pine_bark", "open", "none", "deciduous", "commercial_caution", "St Johns", "Potato/hort belt, limited blueberry."),
        _s("us-fl-live-oak", "Live Oak", "US", "US-SE", "Florida", 30.29, -82.98, "high_chill_shb", "star", "pine_bark", "open", "none", "deciduous", "commercial_success", "Suwannee"),
    ]
)

# --- Georgia rabbiteye / SHB ---
_add(
    [
        _s("us-ga-alma", "Alma", "US", "US-SE", "Georgia", 31.54, -82.46, "rabbiteye", "brightwell", "open_soil", "open", "none", "deciduous", "commercial_success", "Bacon County, US rabbiteye core"),
        _s("us-ga-baxley", "Baxley", "US", "US-SE", "Georgia", 31.78, -82.35, "rabbiteye", "tifblue", "open_soil", "open", "none", "deciduous", "commercial_success", "Appling"),
        _s("us-ga-blackshear", "Blackshear", "US", "US-SE", "Georgia", 31.30, -82.24, "rabbiteye", "brightwell", "open_soil", "open", "none", "deciduous", "commercial_success", "Pierce"),
        _s("us-ga-waycross", "Waycross", "US", "US-SE", "Georgia", 31.21, -82.35, "rabbiteye", "climax", "open_soil", "open", "none", "deciduous", "commercial_success", "Ware"),
        _s("us-ga-homerville", "Homerville", "US", "US-SE", "Georgia", 31.04, -82.75, "rabbiteye", "brightwell", "open_soil", "open", "none", "deciduous", "commercial_success", "Clinch"),
        _s("us-ga-douglas", "Douglas", "US", "US-SE", "Georgia", 31.51, -82.85, "rabbiteye", "ochlockonee", "open_soil", "open", "none", "deciduous", "commercial_success", "Coffee"),
        _s("us-ga-pearson", "Pearson", "US", "US-SE", "Georgia", 31.30, -82.85, "rabbiteye", "brightwell", "open_soil", "open", "none", "deciduous", "commercial_success", "Atkinson"),
        _s("us-ga-nicholls", "Nicholls", "US", "US-SE", "Georgia", 31.52, -82.64, "rabbiteye", "tifblue", "open_soil", "open", "none", "deciduous", "commercial_success", "Coffee"),
        _s("us-ga-ocilla", "Ocilla", "US", "US-SE", "Georgia", 31.59, -83.25, "rabbiteye", "brightwell", "open_soil", "open", "none", "deciduous", "commercial_success", "Irwin"),
        _s("us-ga-fitzgerald", "Fitzgerald", "US", "US-SE", "Georgia", 31.71, -83.25, "rabbiteye", "ochlockonee", "open_soil", "open", "none", "deciduous", "commercial_success", "Ben Hill"),
        _s("us-ga-tifton", "Tifton", "US", "US-SE", "Georgia", 31.45, -83.51, "rabbiteye", "brightwell", "open_soil", "open", "none", "deciduous", "commercial_success", "UGA Tifton"),
        _s("us-ga-nashville", "Nashville GA", "US", "US-SE", "Georgia", 31.21, -83.25, "rabbiteye", "climax", "open_soil", "open", "none", "deciduous", "commercial_success", "Berrien"),
        _s("us-ga-lakeland", "Lakeland GA", "US", "US-SE", "Georgia", 31.04, -83.07, "rabbiteye", "brightwell", "open_soil", "open", "none", "deciduous", "commercial_success", "Lanier"),
        _s("us-ga-valdosta", "Valdosta", "US", "US-SE", "Georgia", 30.83, -83.28, "high_chill_shb", "rebel", "open_soil", "open", "none", "deciduous", "commercial_success", "Lowndes SHB"),
        _s("us-ga-statesboro", "Statesboro", "US", "US-SE", "Georgia", 32.45, -81.78, "rabbiteye", "tifblue", "open_soil", "open", "none", "deciduous", "commercial_success", "Bulloch"),
        _s("us-ga-vidalia", "Vidalia", "US", "US-SE", "Georgia", 32.22, -82.41, "rabbiteye", "brightwell", "open_soil", "open", "none", "deciduous", "commercial_success", "Toombs"),
        _s("us-ga-alapaha", "Alapaha", "US", "US-SE", "Georgia", 31.38, -83.22, "high_chill_shb", "suziblue", "open_soil", "open", "none", "deciduous", "commercial_success", "Berrien SHB"),
        _s("us-ga-broxton", "Broxton", "US", "US-SE", "Georgia", 31.63, -82.89, "rabbiteye", "ochlockonee", "open_soil", "open", "none", "deciduous", "commercial_success", "Coffee"),
        _s("us-ga-jesup", "Jesup", "US", "US-SE", "Georgia", 31.61, -81.88, "rabbiteye", "brightwell", "open_soil", "open", "none", "deciduous", "commercial_success", "Wayne"),
        _s("us-ga-douglas-shb", "Douglas SHB", "US", "US-SE", "Georgia", 31.48, -82.83, "high_chill_shb", "rebel", "open_soil", "open", "none", "deciduous", "commercial_success", "Coffee SHB plantings"),
    ]
)

# --- North Carolina ---
_add(
    [
        _s("us-nc-burgaw", "Burgaw", "US", "US-SE", "North Carolina", 34.55, -77.92, "high_chill_shb", "legacy", "open_soil", "open", "none", "deciduous", "commercial_success", "Pender, NC blueberry belt"),
        _s("us-nc-ivanhoe", "Ivanhoe", "US", "US-SE", "North Carolina", 34.58, -78.25, "rabbiteye", "tifblue", "open_soil", "open", "none", "deciduous", "commercial_success", "Sampson/Bladen edge"),
        _s("us-nc-atkinson", "Atkinson", "US", "US-SE", "North Carolina", 34.53, -78.17, "high_chill_shb", "legacy", "open_soil", "open", "none", "deciduous", "commercial_success", "Pender"),
        _s("us-nc-white-lake", "White Lake", "US", "US-SE", "North Carolina", 34.64, -78.49, "rabbiteye", "brightwell", "open_soil", "open", "none", "deciduous", "commercial_success", "Bladen"),
        _s("us-nc-elizabethtown", "Elizabethtown", "US", "US-SE", "North Carolina", 34.63, -78.61, "rabbiteye", "ochlockonee", "open_soil", "open", "none", "deciduous", "commercial_success", "Bladen"),
        _s("us-nc-bladenboro", "Bladenboro", "US", "US-SE", "North Carolina", 34.54, -78.79, "rabbiteye", "tifblue", "open_soil", "open", "none", "deciduous", "commercial_success", "Bladen"),
        _s("us-nc-clarkton", "Clarkton", "US", "US-SE", "North Carolina", 34.49, -78.66, "high_chill_shb", "legacy", "open_soil", "open", "none", "deciduous", "commercial_success", "Bladen"),
        _s("us-nc-garland", "Garland", "US", "US-SE", "North Carolina", 34.79, -78.43, "rabbiteye", "brightwell", "open_soil", "open", "none", "deciduous", "commercial_success", "Sampson"),
        _s("us-nc-clinton", "Clinton NC", "US", "US-SE", "North Carolina", 35.00, -78.32, "rabbiteye", "tifblue", "open_soil", "open", "none", "deciduous", "commercial_success", "Sampson"),
        _s("us-nc-magnolia", "Magnolia", "US", "US-SE", "North Carolina", 34.90, -78.05, "high_chill_shb", "legacy", "open_soil", "open", "none", "deciduous", "commercial_success", "Duplin"),
        _s("us-nc-rose-hill", "Rose Hill", "US", "US-SE", "North Carolina", 34.82, -78.02, "rabbiteye", "brightwell", "open_soil", "open", "none", "deciduous", "commercial_success", "Duplin"),
        _s("us-nc-wallace", "Wallace", "US", "US-SE", "North Carolina", 34.74, -77.99, "high_chill_shb", "legacy", "open_soil", "open", "none", "deciduous", "commercial_success", "Duplin"),
        _s("us-nc-kenansville", "Kenansville", "US", "US-SE", "North Carolina", 34.96, -77.96, "rabbiteye", "ochlockonee", "open_soil", "open", "none", "deciduous", "commercial_success", "Duplin"),
        _s("us-nc-warsaw", "Warsaw", "US", "US-SE", "North Carolina", 35.00, -78.09, "rabbiteye", "tifblue", "open_soil", "open", "none", "deciduous", "commercial_success", "Duplin"),
        _s("us-nc-faison", "Faison", "US", "US-SE", "North Carolina", 35.12, -78.14, "high_chill_shb", "star", "open_soil", "open", "none", "deciduous", "commercial_success", "Duplin"),
        _s("us-nc-burgundy", "Ivanhoe south", "US", "US-SE", "North Carolina", 34.52, -78.28, "nhb", "legacy", "open_soil", "open", "none", "deciduous", "commercial_caution", "Northern cultivars at NC latitude"),
        _s("us-nc-whiteville", "Whiteville", "US", "US-SE", "North Carolina", 34.34, -78.70, "rabbiteye", "brightwell", "open_soil", "open", "none", "deciduous", "commercial_success", "Columbus"),
        _s("us-nc-tabor", "Tabor City", "US", "US-SE", "North Carolina", 34.15, -78.88, "rabbiteye", "climax", "open_soil", "open", "none", "deciduous", "commercial_success", "Columbus"),
    ]
)

# --- South Carolina / Alabama / Mississippi ---
_add(
    [
        _s("us-sc-loris", "Loris", "US", "US-SE", "South Carolina", 34.06, -78.89, "rabbiteye", "brightwell", "open_soil", "open", "none", "deciduous", "commercial_success", "Horry"),
        _s("us-sc-conway", "Conway", "US", "US-SE", "South Carolina", 33.84, -79.05, "rabbiteye", "tifblue", "open_soil", "open", "none", "deciduous", "commercial_success", "Horry"),
        _s("us-sc-hemingway", "Hemingway", "US", "US-SE", "South Carolina", 33.75, -79.45, "rabbiteye", "ochlockonee", "open_soil", "open", "none", "deciduous", "commercial_success", "Williamsburg"),
        _s("us-sc-johnsonville", "Johnsonville", "US", "US-SE", "South Carolina", 33.82, -79.45, "rabbiteye", "brightwell", "open_soil", "open", "none", "deciduous", "commercial_success", "Florence"),
        _s("us-sc-lake-city", "Lake City SC", "US", "US-SE", "South Carolina", 33.87, -79.75, "rabbiteye", "tifblue", "open_soil", "open", "none", "deciduous", "commercial_success", "Florence"),
        _s("us-sc-moncks", "Moncks Corner", "US", "US-SE", "South Carolina", 33.20, -80.01, "rabbiteye", "climax", "open_soil", "open", "none", "deciduous", "commercial_success", "Berkeley"),
        _s("us-al-fairhope", "Fairhope", "US", "US-SE", "Alabama", 30.52, -87.90, "rabbiteye", "brightwell", "open_soil", "open", "none", "deciduous", "commercial_success", "Baldwin"),
        _s("us-al-foley", "Foley", "US", "US-SE", "Alabama", 30.41, -87.68, "low_chill_shb", "biloxi", "open_soil", "open", "none", "deciduous", "commercial_success", "Baldwin Gulf"),
        _s("us-ms-poplarville", "Poplarville", "US", "US-SE", "Mississippi", 30.84, -89.53, "rabbiteye", "tifblue", "open_soil", "open", "none", "deciduous", "commercial_success", "USDA Poplarville"),
        _s("us-ms-wiggins", "Wiggins", "US", "US-SE", "Mississippi", 30.86, -89.14, "rabbiteye", "brightwell", "open_soil", "open", "none", "deciduous", "commercial_success", "Stone"),
        _s("us-ms-hattiesburg", "Hattiesburg", "US", "US-SE", "Mississippi", 31.33, -89.29, "rabbiteye", "ochlockonee", "open_soil", "open", "none", "deciduous", "commercial_success", "Forrest"),
        _s("us-ar-springdale", "Springdale", "US", "US-SE", "Arkansas", 36.19, -94.13, "nhb", "duke", "open_soil", "open", "none", "deciduous", "commercial_caution", "Limited Ozark plantings"),
    ]
)

# --- Michigan NHB ---
_add(
    [
        _s("us-mi-grand-junction", "Grand Junction", "US", "US-MI", "Michigan", 42.40, -86.08, "nhb", "duke", "open_soil", "open", "none", "deciduous", "commercial_success", "Van Buren, US NHB core"),
        _s("us-mi-south-haven", "South Haven", "US", "US-MI", "Michigan", 42.40, -86.27, "nhb", "bluecrop", "open_soil", "open", "none", "deciduous", "commercial_success", "Van Buren"),
        _s("us-mi-covert", "Covert", "US", "US-MI", "Michigan", 42.29, -86.26, "nhb", "draper", "open_soil", "open", "none", "deciduous", "commercial_success", "Van Buren"),
        _s("us-mi-bangor", "Bangor MI", "US", "US-MI", "Michigan", 42.31, -86.11, "nhb", "elliott", "open_soil", "open", "none", "deciduous", "commercial_success", "Van Buren"),
        _s("us-mi-hartford", "Hartford", "US", "US-MI", "Michigan", 42.21, -86.17, "nhb", "duke", "open_soil", "open", "none", "deciduous", "commercial_success", "Van Buren"),
        _s("us-mi-watervliet", "Watervliet", "US", "US-MI", "Michigan", 42.19, -86.26, "nhb", "bluecrop", "open_soil", "open", "none", "deciduous", "commercial_success", "Berrien"),
        _s("us-mi-coloma", "Coloma", "US", "US-MI", "Michigan", 42.19, -86.31, "nhb", "draper", "open_soil", "open", "none", "deciduous", "commercial_success", "Berrien"),
        _s("us-mi-benton-harbor", "Benton Harbor", "US", "US-MI", "Michigan", 42.12, -86.45, "nhb", "duke", "open_soil", "open", "none", "deciduous", "commercial_success", "Berrien"),
        _s("us-mi-holland", "Holland", "US", "US-MI", "Michigan", 42.79, -86.11, "nhb", "aurora", "open_soil", "open", "none", "deciduous", "commercial_success", "Ottawa"),
        _s("us-mi-west-olive", "West Olive", "US", "US-MI", "Michigan", 42.92, -86.14, "nhb", "elliott", "open_soil", "open", "none", "deciduous", "commercial_success", "Ottawa"),
        _s("us-mi-fennville", "Fennville", "US", "US-MI", "Michigan", 42.59, -86.10, "nhb", "bluecrop", "open_soil", "open", "none", "deciduous", "commercial_success", "Allegan"),
        _s("us-mi-saugatuck", "Saugatuck", "US", "US-MI", "Michigan", 42.65, -86.20, "nhb", "duke", "open_soil", "open", "none", "deciduous", "commercial_success", "Allegan"),
        _s("us-mi-pullman", "Pullman", "US", "US-MI", "Michigan", 42.48, -86.09, "nhb", "draper", "open_soil", "open", "none", "deciduous", "commercial_success", "Allegan"),
        _s("us-mi-bloomingdale", "Bloomingdale", "US", "US-MI", "Michigan", 42.38, -85.96, "nhb", "legacy", "open_soil", "open", "none", "deciduous", "commercial_caution", "Inland, fruit-bud winter kill risk"),
        _s("us-mi-gobles", "Gobles", "US", "US-MI", "Michigan", 42.36, -85.88, "nhb", "draper", "open_soil", "open", "none", "deciduous", "commercial_caution", "Inland Michigan"),
        _s("us-mi-lawton", "Lawton", "US", "US-MI", "Michigan", 42.17, -85.85, "nhb", "bluecrop", "open_soil", "open", "none", "deciduous", "commercial_success", "Van Buren inland"),
        _s("us-mi-paw-paw", "Paw Paw", "US", "US-MI", "Michigan", 42.22, -85.89, "nhb", "duke", "open_soil", "open", "none", "deciduous", "commercial_success", "Van Buren"),
        _s("us-mi-dowagiac", "Dowagiac", "US", "US-MI", "Michigan", 41.98, -86.11, "nhb", "elliott", "open_soil", "open", "none", "deciduous", "commercial_success", "Cass"),
        _s("us-mi-niles", "Niles", "US", "US-MI", "Michigan", 41.83, -86.25, "nhb", "bluecrop", "open_soil", "open", "none", "deciduous", "commercial_success", "Berrien/Cass"),
        _s("us-mi-berrien-springs", "Berrien Springs", "US", "US-MI", "Michigan", 41.95, -86.34, "nhb", "duke", "open_soil", "open", "none", "deciduous", "commercial_success", "Berrien"),
        _s("us-mi-allegan", "Allegan", "US", "US-MI", "Michigan", 42.53, -85.86, "nhb", "aurora", "open_soil", "open", "none", "deciduous", "commercial_caution", "Inland"),
        _s("us-mi-inland-legacy", "Inland Allegan Legacy", "US", "US-MI", "Michigan", 42.55, -85.70, "high_chill_shb", "legacy", "open_soil", "open", "none", "deciduous", "known_failure", "Inland Michigan winter kills Legacy fruit buds"),
    ]
)

# --- Oregon / Washington PNW ---
_add(
    [
        _s("us-or-corvallis", "Corvallis", "US", "US-PNW", "Oregon", 44.56, -123.26, "nhb", "duke", "open_soil", "open", "none", "deciduous", "commercial_success", "OSU / Willamette"),
        _s("us-or-albany", "Albany", "US", "US-PNW", "Oregon", 44.64, -123.11, "nhb", "draper", "open_soil", "open", "none", "deciduous", "commercial_success", "Linn"),
        _s("us-or-salem", "Salem", "US", "US-PNW", "Oregon", 44.94, -123.04, "nhb", "bluecrop", "open_soil", "open", "none", "deciduous", "commercial_success", "Marion"),
        _s("us-or-woodburn", "Woodburn", "US", "US-PNW", "Oregon", 45.14, -122.86, "nhb", "duke", "open_soil", "open", "none", "deciduous", "commercial_success", "Marion"),
        _s("us-or-hubbard", "Hubbard", "US", "US-PNW", "Oregon", 45.18, -122.81, "nhb", "elliott", "open_soil", "open", "none", "deciduous", "commercial_success", "Marion"),
        _s("us-or-canby", "Canby", "US", "US-PNW", "Oregon", 45.26, -122.69, "nhb", "draper", "open_soil", "open", "none", "deciduous", "commercial_success", "Clackamas"),
        _s("us-or-molalla", "Molalla", "US", "US-PNW", "Oregon", 45.15, -122.58, "nhb", "aurora", "open_soil", "open", "none", "deciduous", "commercial_success", "Clackamas"),
        _s("us-or-silverton", "Silverton", "US", "US-PNW", "Oregon", 45.01, -122.78, "nhb", "bluecrop", "open_soil", "open", "none", "deciduous", "commercial_success", "Marion"),
        _s("us-or-lebanon", "Lebanon", "US", "US-PNW", "Oregon", 44.54, -122.91, "nhb", "duke", "open_soil", "open", "none", "deciduous", "commercial_success", "Linn"),
        _s("us-or-junction-city", "Junction City", "US", "US-PNW", "Oregon", 44.22, -123.20, "nhb", "draper", "open_soil", "open", "none", "deciduous", "commercial_success", "Lane"),
        _s("us-or-eugene", "Eugene", "US", "US-PNW", "Oregon", 44.05, -123.09, "nhb", "bluecrop", "open_soil", "open", "none", "deciduous", "commercial_success", "Lane"),
        _s("us-or-harrisburg", "Harrisburg", "US", "US-PNW", "Oregon", 44.27, -123.17, "nhb", "legacy", "open_soil", "open", "none", "deciduous", "commercial_success", "Linn, hybrid exception"),
        _s("us-or-independence", "Independence", "US", "US-PNW", "Oregon", 44.85, -123.19, "nhb", "duke", "open_soil", "open", "none", "deciduous", "commercial_success", "Polk"),
        _s("us-or-mcminnville", "McMinnville", "US", "US-PNW", "Oregon", 45.21, -123.20, "nhb", "elliott", "open_soil", "open", "none", "deciduous", "commercial_success", "Yamhill"),
        _s("us-or-newberg", "Newberg", "US", "US-PNW", "Oregon", 45.30, -122.97, "nhb", "draper", "open_soil", "open", "none", "deciduous", "commercial_success", "Yamhill"),
        _s("us-or-hillsboro", "Hillsboro", "US", "US-PNW", "Oregon", 45.52, -122.99, "nhb", "aurora", "open_soil", "open", "none", "deciduous", "commercial_success", "Washington"),
        _s("us-or-forest-grove", "Forest Grove", "US", "US-PNW", "Oregon", 45.52, -123.11, "nhb", "bluecrop", "open_soil", "open", "none", "deciduous", "commercial_success", "Washington"),
        _s("us-or-sherwood", "Sherwood", "US", "US-PNW", "Oregon", 45.36, -122.84, "nhb", "duke", "open_soil", "open", "none", "deciduous", "commercial_success", "Washington"),
        _s("us-or-willamette-emerald", "Willamette Emerald", "US", "US-PNW", "Oregon", 44.70, -123.10, "low_chill_shb", "emerald", "open_soil", "open", "none", "deciduous", "known_failure", "OSU: do not plant Emerald in the Willamette"),
        _s("us-or-willamette-biloxi", "Willamette Biloxi", "US", "US-PNW", "Oregon", 44.85, -123.05, "low_chill_shb", "biloxi", "open_soil", "open", "none", "deciduous", "known_failure", "OSU: do not plant Biloxi in the Willamette"),
        _s("us-or-willamette-snowchaser", "Willamette Snowchaser", "US", "US-PNW", "Oregon", 45.00, -122.90, "low_chill_shb", "snowchaser", "open_soil", "open", "none", "deciduous", "known_failure", "OSU: do not plant Snowchaser in the Willamette"),
        _s("us-wa-lynden", "Lynden", "US", "US-PNW", "Washington", 48.95, -122.45, "nhb", "duke", "open_soil", "open", "none", "deciduous", "commercial_success", "Whatcom, largest WA district"),
        _s("us-wa-ferndale", "Ferndale", "US", "US-PNW", "Washington", 48.85, -122.59, "nhb", "draper", "open_soil", "open", "none", "deciduous", "commercial_success", "Whatcom"),
        _s("us-wa-everson", "Everson", "US", "US-PNW", "Washington", 48.92, -122.34, "nhb", "bluecrop", "open_soil", "open", "none", "deciduous", "commercial_success", "Whatcom"),
        _s("us-wa-sumas", "Sumas", "US", "US-PNW", "Washington", 48.99, -122.26, "nhb", "elliott", "open_soil", "open", "none", "deciduous", "commercial_success", "Whatcom"),
        _s("us-wa-blaine", "Blaine", "US", "US-PNW", "Washington", 48.99, -122.75, "nhb", "aurora", "open_soil", "open", "none", "deciduous", "commercial_success", "Whatcom"),
        _s("us-wa-mount-vernon", "Mount Vernon", "US", "US-PNW", "Washington", 48.42, -122.33, "nhb", "duke", "open_soil", "open", "none", "deciduous", "commercial_success", "Skagit"),
        _s("us-wa-burlington", "Burlington", "US", "US-PNW", "Washington", 48.48, -122.33, "nhb", "draper", "open_soil", "open", "none", "deciduous", "commercial_success", "Skagit"),
        _s("us-wa-sedro", "Sedro-Woolley", "US", "US-PNW", "Washington", 48.50, -122.24, "nhb", "bluecrop", "open_soil", "open", "none", "deciduous", "commercial_success", "Skagit"),
        _s("us-wa-bow", "Bow", "US", "US-PNW", "Washington", 48.56, -122.40, "nhb", "elliott", "open_soil", "open", "none", "deciduous", "commercial_success", "Skagit"),
        _s("us-wa-conway", "Conway", "US", "US-PNW", "Washington", 48.34, -122.34, "nhb", "duke", "open_soil", "open", "none", "deciduous", "commercial_success", "Skagit"),
    ]
)

# --- British Columbia ---
_add(
    [
        _s("ca-bc-abbotsford", "Abbotsford", "CA", "CA-BC", "British Columbia", 49.05, -122.29, "nhb", "duke", "open_soil", "open", "none", "deciduous", "commercial_success", "Fraser Valley"),
        _s("ca-bc-pitt-meadows", "Pitt Meadows", "CA", "CA-BC", "British Columbia", 49.23, -122.69, "nhb", "draper", "open_soil", "open", "none", "deciduous", "commercial_success", "Metro Vancouver"),
        _s("ca-bc-maple-ridge", "Maple Ridge", "CA", "CA-BC", "British Columbia", 49.22, -122.60, "nhb", "bluecrop", "open_soil", "open", "none", "deciduous", "commercial_success", "Fraser"),
        _s("ca-bc-mission", "Mission", "CA", "CA-BC", "British Columbia", 49.13, -122.31, "nhb", "elliott", "open_soil", "open", "none", "deciduous", "commercial_success", "Fraser"),
        _s("ca-bc-chilliwack", "Chilliwack", "CA", "CA-BC", "British Columbia", 49.17, -121.95, "nhb", "duke", "open_soil", "open", "none", "deciduous", "commercial_success", "Fraser"),
        _s("ca-bc-langley", "Langley", "CA", "CA-BC", "British Columbia", 49.10, -122.66, "nhb", "draper", "open_soil", "open", "none", "deciduous", "commercial_success", "Fraser"),
        _s("ca-bc-surrey", "Surrey", "CA", "CA-BC", "British Columbia", 49.10, -122.80, "nhb", "bluecrop", "open_soil", "open", "none", "deciduous", "commercial_success", "Fraser"),
        _s("ca-bc-richmond", "Richmond", "CA", "CA-BC", "British Columbia", 49.17, -123.14, "nhb", "aurora", "open_soil", "open", "none", "deciduous", "commercial_caution", "Urban edge, peat soils"),
        _s("ca-bc-delta", "Delta", "CA", "CA-BC", "British Columbia", 49.08, -123.06, "nhb", "duke", "open_soil", "open", "none", "deciduous", "commercial_success", "Fraser delta"),
        _s("ca-bc-aldergrove", "Aldergrove", "CA", "CA-BC", "British Columbia", 49.06, -122.47, "nhb", "draper", "open_soil", "open", "none", "deciduous", "commercial_success", "Langley township"),
        _s("ca-bc-agassiz", "Agassiz", "CA", "CA-BC", "British Columbia", 49.24, -121.77, "nhb", "elliott", "open_soil", "open", "none", "deciduous", "commercial_success", "Fraser east"),
        _s("ca-bc-matsqui", "Matsqui", "CA", "CA-BC", "British Columbia", 49.08, -122.30, "nhb", "bluecrop", "open_soil", "open", "none", "deciduous", "commercial_success", "Abbotsford"),
    ]
)

# --- Chile ---
_add(
    [
        _s("cl-osorno", "Osorno", "CL", "CL-SOUTH", "Los Lagos", -40.57, -73.15, "high_chill_shb", "legacy", "open_soil", "open", "net", "deciduous", "commercial_success", "ODEPA / Chile largest Legacy belt"),
        _s("cl-la-union", "La Unión", "CL", "CL-SOUTH", "Los Ríos", -40.29, -73.08, "high_chill_shb", "legacy", "open_soil", "open", "net", "deciduous", "commercial_success", "ODEPA"),
        _s("cl-rio-bueno", "Río Bueno", "CL", "CL-SOUTH", "Los Ríos", -40.33, -72.96, "high_chill_shb", "legacy", "open_soil", "open", "woven", "deciduous", "commercial_success", "Matamala cover region"),
        _s("cl-lanco", "Lanco", "CL", "CL-SOUTH", "Los Ríos", -39.45, -72.78, "high_chill_shb", "top_shelf", "open_soil", "open", "net", "deciduous", "commercial_success", "Los Ríos"),
        _s("cl-valdivia", "Valdivia hinterland", "CL", "CL-SOUTH", "Los Ríos", -39.82, -73.05, "high_chill_shb", "legacy", "open_soil", "open", "net", "deciduous", "commercial_success", "Los Ríos"),
        _s("cl-paillaco", "Paillaco", "CL", "CL-SOUTH", "Los Ríos", -40.07, -72.87, "high_chill_shb", "legacy", "open_soil", "open", "none", "deciduous", "commercial_success", "Los Ríos"),
        _s("cl-purranque", "Purranque", "CL", "CL-SOUTH", "Los Lagos", -40.92, -73.16, "high_chill_shb", "legacy", "open_soil", "open", "net", "deciduous", "commercial_success", "Osorno south"),
        _s("cl-frutillar", "Frutillar", "CL", "CL-SOUTH", "Los Lagos", -41.12, -73.06, "nhb", "duke", "open_soil", "open", "net", "deciduous", "commercial_success", "Llanquihue"),
        _s("cl-puerto-varas", "Puerto Varas", "CL", "CL-SOUTH", "Los Lagos", -41.32, -72.99, "nhb", "draper", "open_soil", "open", "net", "deciduous", "commercial_success", "Llanquihue"),
        _s("cl-llanquihue", "Llanquihue", "CL", "CL-SOUTH", "Los Lagos", -41.26, -73.01, "high_chill_shb", "legacy", "open_soil", "open", "woven", "deciduous", "commercial_success", "Matamala-type covers"),
        _s("cl-puerto-montt", "Puerto Montt hinterland", "CL", "CL-SOUTH", "Los Lagos", -41.47, -72.94, "nhb", "bluecrop", "open_soil", "open", "net", "deciduous", "commercial_caution", "Cool, wet, late"),
        _s("cl-temuco", "Temuco", "CL", "CL-SOUTH", "Araucanía", -38.74, -72.60, "high_chill_shb", "legacy", "open_soil", "open", "none", "deciduous", "commercial_caution", "González-Villagra chamber heat work"),
        _s("cl-villarrica", "Villarrica", "CL", "CL-SOUTH", "Araucanía", -39.28, -72.23, "high_chill_shb", "legacy", "open_soil", "open", "net", "deciduous", "commercial_success", "Araucanía lakes"),
        _s("cl-angol", "Angol", "CL", "CL-SOUTH", "Araucanía", -37.80, -72.71, "high_chill_shb", "legacy", "open_soil", "open", "none", "deciduous", "commercial_success", "Malleco"),
        _s("cl-los-angeles", "Los Ángeles", "CL", "CL-SOUTH", "Biobío", -37.47, -72.35, "high_chill_shb", "legacy", "open_soil", "open", "net", "deciduous", "commercial_success", "Biobío"),
        _s("cl-chillan", "Chillán", "CL", "CL-CENTRAL", "Ñuble", -36.61, -72.10, "high_chill_shb", "legacy", "open_soil", "open", "none", "deciduous", "commercial_success", "Ñuble"),
        _s("cl-linares", "Linares", "CL", "CL-CENTRAL", "Maule", -35.85, -71.60, "high_chill_shb", "top_shelf", "open_soil", "open", "net", "deciduous", "commercial_success", "Maule"),
        _s("cl-cauquenes", "Cauquenes", "CL", "CL-CENTRAL", "Maule", -35.97, -72.32, "high_chill_shb", "legacy", "open_soil", "open", "none", "deciduous", "commercial_caution", "Warmer, drier Maule"),
        _s("cl-curico", "Curicó", "CL", "CL-CENTRAL", "Maule", -34.98, -71.24, "high_chill_shb", "legacy", "open_soil", "open", "none", "deciduous", "commercial_caution", "North of core belt"),
        _s("cl-san-fernando", "San Fernando", "CL", "CL-CENTRAL", "O'Higgins", -34.59, -70.99, "high_chill_shb", "legacy", "open_soil", "open", "none", "deciduous", "commercial_caution", "North limit"),
        _s("cl-constitucion", "Constitución hinterland", "CL", "CL-CENTRAL", "Maule", -35.33, -72.41, "nhb", "duke", "open_soil", "open", "net", "deciduous", "commercial_caution", "Coastal fog / cool"),
        _s("cl-rio-negro", "Río Negro", "CL", "CL-SOUTH", "Los Lagos", -40.80, -73.22, "high_chill_shb", "legacy", "open_soil", "open", "woven", "deciduous", "commercial_success", "Osorno"),
        _s("cl-san-pablo", "San Pablo", "CL", "CL-SOUTH", "Los Lagos", -40.41, -73.01, "high_chill_shb", "legacy", "open_soil", "open", "net", "deciduous", "commercial_success", "Osorno"),
        _s("cl-panguipulli", "Panguipulli", "CL", "CL-SOUTH", "Los Ríos", -39.64, -72.33, "nhb", "draper", "open_soil", "open", "net", "deciduous", "commercial_success", "Lakes"),
        _s("cl-la-union-topshelf", "La Unión Top Shelf", "CL", "CL-SOUTH", "Los Ríos", -40.27, -73.10, "high_chill_shb", "top_shelf", "open_soil", "open", "woven", "deciduous", "commercial_success", "Matamala 2023 covers"),
    ]
)

# --- Peru evergreen substrate ---
_add(
    [
        _s("pe-olmos", "Olmos", "PE", "PE-NORTH", "Lambayeque", -6.00, -79.75, "evergreen_zero_chill", "biloxi_evergreen", "substrate", "open", "net", "evergreen", "commercial_success", "MIDAGRI / Hortifrut-class Olmos"),
        _s("pe-motupe", "Motupe", "PE", "PE-NORTH", "Lambayeque", -6.15, -79.71, "evergreen_zero_chill", "biloxi_evergreen", "substrate", "open", "net", "evergreen", "commercial_success", "Lambayeque"),
        _s("pe-jayanca", "Jayanca", "PE", "PE-NORTH", "Lambayeque", -6.39, -79.82, "evergreen_zero_chill", "biloxi_evergreen", "substrate", "open", "net", "evergreen", "commercial_success", "Lambayeque"),
        _s("pe-ferrenafe", "Ferreñafe", "PE", "PE-NORTH", "Lambayeque", -6.64, -79.79, "evergreen_zero_chill", "ventura", "substrate", "open", "net", "evergreen", "commercial_caution", "Ventura heat flowering fail 2023/24"),
        _s("pe-chiclayo", "Chiclayo hinterland", "PE", "PE-NORTH", "Lambayeque", -6.77, -79.84, "evergreen_zero_chill", "biloxi_evergreen", "substrate", "open", "net", "evergreen", "commercial_success", "Lambayeque"),
        _s("pe-trujillo", "Trujillo / Chao", "PE", "PE-NORTH", "La Libertad", -8.17, -78.99, "evergreen_zero_chill", "biloxi_evergreen", "substrate", "open", "net", "evergreen", "commercial_success", "La Libertad"),
        _s("pe-chao", "Chao", "PE", "PE-NORTH", "La Libertad", -8.54, -78.68, "evergreen_zero_chill", "biloxi_evergreen", "substrate", "open", "net", "evergreen", "commercial_success", "Virú valley"),
        _s("pe-viru", "Virú", "PE", "PE-NORTH", "La Libertad", -8.42, -78.75, "evergreen_zero_chill", "ventura", "substrate", "open", "net", "evergreen", "commercial_caution", "Heat 2023/24"),
        _s("pe-huacho", "Huacho", "PE", "PE-CENTRAL", "Lima", -11.11, -77.61, "evergreen_zero_chill", "biloxi_evergreen", "substrate", "open", "net", "evergreen", "commercial_success", "Huaura"),
        _s("pe-barranca", "Barranca", "PE", "PE-CENTRAL", "Lima", -10.75, -77.76, "evergreen_zero_chill", "biloxi_evergreen", "substrate", "open", "net", "evergreen", "commercial_success", "Lima north"),
        _s("pe-huaura", "Huaura", "PE", "PE-CENTRAL", "Lima", -11.07, -77.60, "evergreen_zero_chill", "biloxi_evergreen", "substrate", "open", "net", "evergreen", "commercial_success", "Huaura"),
        _s("pe-huaral", "Huaral", "PE", "PE-CENTRAL", "Lima", -11.50, -77.21, "evergreen_zero_chill", "biloxi_evergreen", "substrate", "open", "net", "evergreen", "commercial_success", "Lima"),
        _s("pe-canete", "Cañete", "PE", "PE-CENTRAL", "Lima", -13.08, -76.39, "evergreen_zero_chill", "biloxi_evergreen", "substrate", "open", "net", "evergreen", "commercial_success", "Lima south"),
        _s("pe-chincha", "Chincha", "PE", "PE-SOUTH", "Ica", -13.42, -76.13, "evergreen_zero_chill", "biloxi_evergreen", "substrate", "open", "net", "evergreen", "commercial_success", "Ica"),
        _s("pe-pisco", "Pisco", "PE", "PE-SOUTH", "Ica", -13.71, -76.20, "evergreen_zero_chill", "biloxi_evergreen", "substrate", "open", "net", "evergreen", "commercial_success", "Ica"),
        _s("pe-ica", "Ica", "PE", "PE-SOUTH", "Ica", -14.07, -75.73, "evergreen_zero_chill", "biloxi_evergreen", "substrate", "open", "net", "evergreen", "commercial_success", "Ica desert irrigation"),
        _s("pe-ica-ventura", "Ica Ventura", "PE", "PE-SOUTH", "Ica", -14.10, -75.70, "evergreen_zero_chill", "ventura", "substrate", "open", "net", "evergreen", "known_failure", "2023/24 heat flowering failure"),
        _s("pe-olmos-deciduous", "Olmos deciduous Duke", "PE", "PE-NORTH", "Lambayeque", -5.98, -79.78, "nhb", "duke", "substrate", "open", "net", "deciduous", "known_failure", "NHB chill cannot complete on the Peru coast"),
        _s("pe-lambayeque", "Lambayeque", "PE", "PE-NORTH", "Lambayeque", -6.70, -79.91, "evergreen_zero_chill", "biloxi_evergreen", "substrate", "open", "net", "evergreen", "commercial_success", "Lambayeque"),
        _s("pe-chepen", "Chepén", "PE", "PE-NORTH", "La Libertad", -7.23, -79.45, "evergreen_zero_chill", "biloxi_evergreen", "substrate", "open", "net", "evergreen", "commercial_success", "La Libertad"),
    ]
)

# --- Mexico ---
_add(
    [
        _s("mx-zapopan", "Zapotlán / Ciudad Guzmán", "MX", "MX-JAL", "Jalisco", 19.70, -103.46, "low_chill_shb", "biloxi", "open_soil", "open", "net", "deciduous", "commercial_success", "Jalisco highland belt"),
        _s("mx-sayula", "Sayula", "MX", "MX-JAL", "Jalisco", 19.88, -103.60, "low_chill_shb", "biloxi", "substrate", "open", "net", "deciduous", "commercial_success", "Jalisco"),
        _s("mx-tapalpa", "Tapalpa", "MX", "MX-JAL", "Jalisco", 19.94, -103.76, "low_chill_shb", "emerald", "open_soil", "open", "net", "deciduous", "commercial_success", "Jalisco cool highland"),
        _s("mx-autlan", "Autlán", "MX", "MX-JAL", "Jalisco", 19.77, -104.37, "evergreen_zero_chill", "biloxi_evergreen", "substrate", "open", "net", "evergreen", "commercial_success", "Jalisco"),
        _s("mx-ciudad-guzman", "Ciudad Guzmán east", "MX", "MX-JAL", "Jalisco", 19.72, -103.46, "low_chill_shb", "jewel", "open_soil", "open", "none", "deciduous", "commercial_success", "Jalisco"),
        _s("mx-encarnacion", "Encarnación de Díaz", "MX", "MX-JAL", "Jalisco", 21.53, -102.24, "high_chill_shb", "star", "open_soil", "open", "none", "deciduous", "commercial_caution", "Los Altos, frost"),
        _s("mx-culiacan", "Culiacán", "MX", "MX-SIN", "Sinaloa", 24.81, -107.39, "evergreen_zero_chill", "biloxi_evergreen", "substrate", "open", "net", "evergreen", "commercial_success", "Sinaloa"),
        _s("mx-los-mochis", "Los Mochis", "MX", "MX-SIN", "Sinaloa", 25.79, -108.99, "evergreen_zero_chill", "biloxi_evergreen", "substrate", "open", "net", "evergreen", "commercial_success", "Sinaloa"),
        _s("mx-guasave", "Guasave", "MX", "MX-SIN", "Sinaloa", 25.57, -108.47, "evergreen_zero_chill", "biloxi_evergreen", "substrate", "open", "net", "evergreen", "commercial_success", "Sinaloa"),
        _s("mx-ensenada", "Ensenada", "MX", "MX-BCN", "Baja California", 31.87, -116.60, "low_chill_shb", "biloxi", "open_soil", "open", "net", "deciduous", "commercial_success", "Baja coast"),
        _s("mx-san-quintin", "San Quintín", "MX", "MX-BCN", "Baja California", 30.56, -115.94, "low_chill_shb", "emerald", "substrate", "open", "net", "deciduous", "commercial_success", "Baja"),
        _s("mx-vicente-guerrero", "Vicente Guerrero", "MX", "MX-BCN", "Baja California", 30.73, -115.99, "evergreen_zero_chill", "biloxi_evergreen", "substrate", "open", "net", "evergreen", "commercial_success", "San Quintín valley"),
        _s("mx-colima", "Colima hinterland", "MX", "MX-COL", "Colima", 19.24, -103.72, "low_chill_shb", "biloxi", "open_soil", "open", "net", "deciduous", "commercial_success", "Colima"),
        _s("mx-uruapan", "Uruapan", "MX", "MX-MIC", "Michoacán", 19.41, -102.05, "low_chill_shb", "biloxi", "open_soil", "open", "net", "deciduous", "commercial_caution", "Avocado country, blueberry trials"),
        _s("mx-zamora", "Zamora", "MX", "MX-MIC", "Michoacán", 20.00, -102.28, "low_chill_shb", "emerald", "open_soil", "open", "none", "deciduous", "commercial_caution", "Michoacán"),
    ]
)

# --- Spain Huelva ---
_add(
    [
        _s("es-moguer", "Moguer", "ES", "ES-HUELVA", "Andalucía", 37.28, -6.84, "low_chill_shb", "biloxi", "substrate", "tunnel", "ldpe", "deciduous", "commercial_success", "Huelva core, MAPA"),
        _s("es-lucena", "Lucena del Puerto", "ES", "ES-HUELVA", "Andalucía", 37.30, -6.73, "low_chill_shb", "emerald", "substrate", "tunnel", "ldpe", "deciduous", "commercial_success", "Huelva"),
        _s("es-palos", "Palos de la Frontera", "ES", "ES-HUELVA", "Andalucía", 37.23, -6.89, "evergreen_zero_chill", "biloxi_evergreen", "substrate", "tunnel", "ldpe", "evergreen", "commercial_success", "Huelva"),
        _s("es-almonte", "Almonte", "ES", "ES-HUELVA", "Andalucía", 37.26, -6.52, "low_chill_shb", "jewel", "substrate", "tunnel", "woven", "deciduous", "commercial_success", "Huelva"),
        _s("es-bonares", "Bonares", "ES", "ES-HUELVA", "Andalucía", 37.24, -6.68, "low_chill_shb", "biloxi", "substrate", "tunnel", "ldpe", "deciduous", "commercial_success", "Huelva"),
        _s("es-rociana", "Rociana del Condado", "ES", "ES-HUELVA", "Andalucía", 37.31, -6.60, "low_chill_shb", "emerald", "substrate", "tunnel", "ldpe", "deciduous", "commercial_success", "Huelva"),
        _s("es-niebla", "Niebla", "ES", "ES-HUELVA", "Andalucía", 37.36, -6.68, "low_chill_shb", "star", "substrate", "tunnel", "none", "deciduous", "commercial_caution", "Huelva inland"),
        _s("es-cartaya", "Cartaya", "ES", "ES-HUELVA", "Andalucía", 37.21, -7.15, "low_chill_shb", "biloxi", "substrate", "tunnel", "ldpe", "deciduous", "commercial_success", "Huelva west"),
        _s("es-lepe", "Lepe", "ES", "ES-HUELVA", "Andalucía", 37.25, -7.20, "evergreen_zero_chill", "biloxi_evergreen", "substrate", "tunnel", "ldpe", "evergreen", "commercial_success", "Huelva"),
        _s("es-gibraleon", "Gibraleón", "ES", "ES-HUELVA", "Andalucía", 37.38, -6.97, "low_chill_shb", "emerald", "substrate", "tunnel", "ldpe", "deciduous", "commercial_success", "Huelva"),
        _s("es-bollullos", "Bollullos Par del Condado", "ES", "ES-HUELVA", "Andalucía", 37.34, -6.54, "low_chill_shb", "jewel", "substrate", "tunnel", "woven", "deciduous", "commercial_success", "Huelva"),
        _s("es-villablanca", "Villablanca", "ES", "ES-HUELVA", "Andalucía", 37.30, -7.34, "low_chill_shb", "biloxi", "substrate", "tunnel", "ldpe", "deciduous", "commercial_success", "Huelva/Portugal edge"),
        _s("es-aljaraque", "Aljaraque", "ES", "ES-HUELVA", "Andalucía", 37.27, -7.02, "low_chill_shb", "emerald", "substrate", "tunnel", "ldpe", "deciduous", "commercial_success", "Huelva"),
        _s("es-huelva-city", "Huelva hinterland", "ES", "ES-HUELVA", "Andalucía", 37.26, -6.95, "low_chill_shb", "biloxi", "substrate", "tunnel", "ldpe", "deciduous", "commercial_success", "Huelva"),
    ]
)

# --- Morocco ---
_add(
    [
        _s("ma-larache", "Larache", "MA", "MA-NORTH", "Tanger-Tétouan-Al Hoceima", 35.19, -6.16, "low_chill_shb", "biloxi", "substrate", "tunnel", "ldpe", "deciduous", "commercial_success", "Loukkos"),
        _s("ma-ksar", "Ksar El Kebir", "MA", "MA-NORTH", "Tanger-Tétouan-Al Hoceima", 35.00, -5.90, "low_chill_shb", "emerald", "substrate", "tunnel", "ldpe", "deciduous", "commercial_success", "Loukkos"),
        _s("ma-moulay", "Moulay Bousselham", "MA", "MA-NORTH", "Rabat-Salé-Kénitra", 34.88, -6.29, "evergreen_zero_chill", "biloxi_evergreen", "substrate", "tunnel", "ldpe", "evergreen", "commercial_success", "Gharb coast"),
        _s("ma-kenitra", "Kénitra hinterland", "MA", "MA-NORTH", "Rabat-Salé-Kénitra", 34.26, -6.58, "low_chill_shb", "biloxi", "substrate", "tunnel", "ldpe", "deciduous", "commercial_success", "Gharb"),
        _s("ma-sidi-slimane", "Sidi Slimane", "MA", "MA-NORTH", "Rabat-Salé-Kénitra", 34.26, -5.92, "low_chill_shb", "jewel", "substrate", "tunnel", "ldpe", "deciduous", "commercial_success", "Gharb"),
        _s("ma-sidi-yahya", "Sidi Yahya El Gharb", "MA", "MA-NORTH", "Rabat-Salé-Kénitra", 34.31, -6.30, "low_chill_shb", "emerald", "substrate", "open", "net", "deciduous", "commercial_success", "Gharb"),
        _s("ma-souk-el-arba", "Souk El Arbaa", "MA", "MA-NORTH", "Rabat-Salé-Kénitra", 34.69, -5.99, "low_chill_shb", "biloxi", "substrate", "tunnel", "ldpe", "deciduous", "commercial_success", "Gharb"),
        _s("ma-agadir", "Agadir hinterland", "MA", "MA-SOUTH", "Souss-Massa", 30.43, -9.60, "evergreen_zero_chill", "biloxi_evergreen", "substrate", "open", "net", "evergreen", "commercial_success", "Souss"),
        _s("ma-taroudant", "Taroudant", "MA", "MA-SOUTH", "Souss-Massa", 30.47, -8.88, "evergreen_zero_chill", "biloxi_evergreen", "substrate", "open", "net", "evergreen", "commercial_success", "Souss"),
        _s("ma-ouled-teima", "Ouled Teima", "MA", "MA-SOUTH", "Souss-Massa", 30.39, -9.21, "evergreen_zero_chill", "biloxi_evergreen", "substrate", "tunnel", "ldpe", "evergreen", "commercial_success", "Souss"),
        _s("ma-biougra", "Biougra", "MA", "MA-SOUTH", "Souss-Massa", 30.21, -9.37, "low_chill_shb", "biloxi", "substrate", "tunnel", "ldpe", "deciduous", "commercial_success", "Chtouka"),
        _s("ma-larache-wind", "Larache wind-exposed tunnel", "MA", "MA-NORTH", "Tanger-Tétouan-Al Hoceima", 35.22, -6.20, "low_chill_shb", "biloxi", "substrate", "tunnel", "ldpe", "deciduous", "commercial_caution", "Atlantic wind. Tunnels fail near 110 km/h."),
    ]
)

# --- Australia ---
_add(
    [
        _s("au-coffs", "Coffs Harbour", "AU", "AU-NSW", "New South Wales", -30.30, 153.12, "low_chill_shb", "biloxi", "open_soil", "open", "net", "deciduous", "commercial_success", "NSW north coast"),
        _s("au-woolgoolga", "Woolgoolga", "AU", "AU-NSW", "New South Wales", -30.11, 153.20, "low_chill_shb", "emerald", "open_soil", "open", "net", "deciduous", "commercial_success", "NSW"),
        _s("au-bundaberg", "Bundaberg", "AU", "AU-QLD", "Queensland", -24.87, 152.35, "evergreen_zero_chill", "biloxi_evergreen", "substrate", "open", "net", "evergreen", "commercial_success", "QLD"),
        _s("au-sunshine", "Sunshine Coast hinterland", "AU", "AU-QLD", "Queensland", -26.65, 152.96, "low_chill_shb", "biloxi", "open_soil", "open", "net", "deciduous", "commercial_success", "QLD"),
        _s("au-nambour", "Nambour", "AU", "AU-QLD", "Queensland", -26.63, 152.96, "low_chill_shb", "jewel", "open_soil", "open", "none", "deciduous", "commercial_success", "QLD"),
        _s("au-devonport", "Devonport", "AU", "AU-TAS", "Tasmania", -41.18, 146.35, "nhb", "duke", "open_soil", "open", "net", "deciduous", "commercial_success", "Tas NHB"),
        _s("au-huonville", "Huonville", "AU", "AU-TAS", "Tasmania", -43.03, 147.05, "nhb", "draper", "open_soil", "open", "net", "deciduous", "commercial_success", "Huon"),
        _s("au-grove", "Grove", "AU", "AU-TAS", "Tasmania", -42.98, 147.10, "nhb", "bluecrop", "open_soil", "open", "none", "deciduous", "commercial_success", "Huon TIA"),
        _s("au-spreyton", "Spreyton", "AU", "AU-TAS", "Tasmania", -41.22, 146.35, "nhb", "elliott", "open_soil", "open", "net", "deciduous", "commercial_success", "North Tas"),
        _s("au-mornington", "Mornington Peninsula", "AU", "AU-VIC", "Victoria", -38.22, 145.04, "nhb", "duke", "open_soil", "open", "net", "deciduous", "commercial_success", "VIC"),
        _s("au-gippsland", "West Gippsland", "AU", "AU-VIC", "Victoria", -38.20, 145.90, "nhb", "bluecrop", "open_soil", "open", "net", "deciduous", "commercial_success", "VIC"),
        _s("au-manjimup", "Manjimup", "AU", "AU-WA", "Western Australia", -34.24, 116.15, "nhb", "duke", "open_soil", "open", "net", "deciduous", "commercial_success", "WA south"),
        _s("au-pemberton", "Pemberton", "AU", "AU-WA", "Western Australia", -34.44, 116.03, "nhb", "draper", "open_soil", "open", "net", "deciduous", "commercial_success", "WA"),
        _s("au-albany", "Albany WA", "AU", "AU-WA", "Western Australia", -35.03, 117.88, "nhb", "bluecrop", "open_soil", "open", "none", "deciduous", "commercial_success", "WA south coast"),
    ]
)

# --- New Zealand ---
_add(
    [
        _s("nz-pukekohe", "Pukekohe", "NZ", "NZ-NORTH", "Auckland", -37.20, 174.90, "nhb", "duke", "open_soil", "open", "none", "deciduous", "commercial_success", "Landcare blueberry map region"),
        _s("nz-hamilton", "Hamilton hinterland", "NZ", "NZ-NORTH", "Waikato", -37.79, 175.28, "nhb", "bluecrop", "open_soil", "open", "none", "deciduous", "commercial_success", "Waikato"),
        _s("nz-tauranga", "Tauranga hinterland", "NZ", "NZ-NORTH", "Bay of Plenty", -37.69, 176.17, "nhb", "draper", "open_soil", "open", "net", "deciduous", "commercial_success", "BOP"),
        _s("nz-te-puke", "Te Puke", "NZ", "NZ-NORTH", "Bay of Plenty", -37.78, 176.33, "nhb", "duke", "open_soil", "open", "net", "deciduous", "commercial_success", "BOP"),
        _s("nz-hastings", "Hastings", "NZ", "NZ-NORTH", "Hawke's Bay", -39.64, 176.84, "nhb", "elliott", "open_soil", "open", "none", "deciduous", "commercial_success", "Hawke's Bay"),
        _s("nz-hastings-shb", "Hastings SHB trial", "NZ", "NZ-NORTH", "Hawke's Bay", -39.66, 176.82, "low_chill_shb", "emerald", "open_soil", "open", "none", "deciduous", "commercial_caution", "Landcare one-curve chill is the bar to beat"),
        _s("nz-nelson", "Nelson", "NZ", "NZ-SOUTH", "Nelson", -41.27, 173.28, "nhb", "duke", "open_soil", "open", "none", "deciduous", "commercial_success", "Nelson"),
        _s("nz-motueka", "Motueka", "NZ", "NZ-SOUTH", "Tasman", -41.12, 173.01, "nhb", "draper", "open_soil", "open", "net", "deciduous", "commercial_success", "Tasman"),
        _s("nz-blenheim", "Blenheim", "NZ", "NZ-SOUTH", "Marlborough", -41.51, 173.95, "nhb", "bluecrop", "open_soil", "open", "none", "deciduous", "commercial_success", "Marlborough"),
        _s("nz-rangiora", "Rangiora", "NZ", "NZ-SOUTH", "Canterbury", -43.30, 172.59, "nhb", "aurora", "open_soil", "open", "none", "deciduous", "commercial_success", "Canterbury"),
        _s("nz-lincoln", "Lincoln", "NZ", "NZ-SOUTH", "Canterbury", -43.64, 172.49, "nhb", "duke", "open_soil", "open", "none", "deciduous", "commercial_success", "Landcare / Plant & Food"),
        _s("nz-richmond", "Richmond", "NZ", "NZ-SOUTH", "Tasman", -41.34, 173.18, "nhb", "elliott", "open_soil", "open", "none", "deciduous", "commercial_success", "Tasman"),
    ]
)

# --- Stress tests and horticultural absences ---
_add(
    [
        _s("in-delhi", "Delhi NCR", "IN", "IN-IGP", "Delhi", 28.61, 77.21, "low_chill_shb", "biloxi", "open_soil", "open", "none", "deciduous", "known_failure", "Smith 2023 IGP fog", "Temperature-and-chill model greens this. Winter DLI crash and wet flowers do not."),
        _s("in-lucknow", "Lucknow", "IN", "IN-IGP", "Uttar Pradesh", 26.85, 80.95, "low_chill_shb", "emerald", "open_soil", "open", "none", "deciduous", "known_failure", "Smith 2023, 39 fog events/yr"),
        _s("in-patna", "Patna", "IN", "IN-IGP", "Bihar", 25.61, 85.14, "low_chill_shb", "snowchaser", "open_soil", "open", "none", "deciduous", "known_failure", "Smith 2023, 45 fog events/yr"),
        _s("in-kanpur", "Kanpur", "IN", "IN-IGP", "Uttar Pradesh", 26.45, 80.33, "evergreen_zero_chill", "biloxi_evergreen", "open_soil", "open", "none", "evergreen", "known_failure", "Bharali 2024 winter SW already cut about 19%"),
        _s("ke-nairobi", "Nairobi highland trial", "KE", "AF-EA", "Nairobi", -1.29, 36.82, "low_chill_shb", "biloxi", "open_soil", "open", "none", "deciduous", "commercial_caution", "Hemp 2024 mountain climate warning", "WorldClim/CHELSA fail tropical mountains. Hypothesis only."),
        _s("tz-moshi", "Moshi / Kilimanjaro slope", "TZ", "AF-EA", "Kilimanjaro", -3.35, 37.33, "low_chill_shb", "emerald", "open_soil", "open", "none", "deciduous", "commercial_caution", "Hemp 2024 MAP mismatch"),
        _s("us-ia-ames", "Ames corn belt", "US", "US-MW", "Iowa", 42.03, -93.62, "nhb", "duke", "open_soil", "open", "none", "deciduous", "horticultural_absence", "US NASS: hort land, not blueberry"),
        _s("us-ks-manhattan", "Manhattan KS", "US", "US-MW", "Kansas", 39.18, -96.57, "nhb", "bluecrop", "open_soil", "open", "none", "deciduous", "horticultural_absence", "Wheat/hort, not blueberry"),
        _s("us-il-urbana", "Urbana", "US", "US-MW", "Illinois", 40.11, -88.21, "nhb", "duke", "open_soil", "open", "none", "deciduous", "horticultural_absence", "Corn belt hort"),
        _s("us-ca-salinas", "Salinas strawberry fog", "US", "US-CA", "California", 36.68, -121.66, "low_chill_shb", "biloxi", "open_soil", "open", "none", "deciduous", "commercial_caution", "Baguskas 2021 marine fog is not IGP fog"),
        _s("us-ca-watsonville", "Watsonville", "US", "US-CA", "California", 36.91, -121.76, "low_chill_shb", "emerald", "open_soil", "open", "none", "deciduous", "commercial_caution", "Limited CA blueberry vs berries"),
        _s("fr-bordeaux", "Bordeaux hinterland", "FR", "EU-ATL", "Nouvelle-Aquitaine", 44.84, -0.58, "nhb", "duke", "open_soil", "open", "none", "deciduous", "horticultural_absence", "Wine hort, not blueberry belt"),
        _s("it-verona", "Verona", "IT", "EU-MED", "Veneto", 45.44, 10.99, "nhb", "bluecrop", "open_soil", "open", "none", "deciduous", "horticultural_absence", "Fruit hort, sparse blueberry"),
        _s("cn-fuzhou", "Fuzhou", "CN", "CN-SE", "Fujian", 26.07, 119.30, "low_chill_shb", "biloxi", "open_soil", "open", "none", "deciduous", "commercial_caution", "Fujian expert-weight GIS is a baseline, not truth"),
        _s("cn-guiyang", "Guiyang", "CN", "CN-SW", "Guizhou", 26.65, 106.63, "high_chill_shb", "legacy", "open_soil", "open", "none", "deciduous", "commercial_caution", "Guizhou CatBoost local presence"),
        _s("uk-kent", "Kent", "GB", "EU-ATL", "England", 51.28, 0.52, "nhb", "duke", "open_soil", "open", "none", "deciduous", "commercial_caution", "UK field blueberry, not Matrix-GS"),
        _s("uk-ford", "Ford / Arundel glasshouse", "GB", "EU-ATL", "England", 50.82, -0.58, "evergreen_zero_chill", "biloxi_evergreen", "substrate", "greenhouse", "none", "evergreen", "commercial_caution", "EBC Matrix-GS neighbour", "Energy and grid, not outdoor climate. 26 ha expansion blocked to 2037."),
        _s("za-stellenbosch", "Stellenbosch", "ZA", "AF-SA", "Western Cape", -33.93, 18.86, "low_chill_shb", "emerald", "open_soil", "open", "net", "deciduous", "commercial_caution", "Cape hort, emerging blueberry"),
        _s("ar-tucuman", "Tucumán", "AR", "AR-NW", "Tucumán", -26.82, -65.22, "low_chill_shb", "biloxi", "open_soil", "open", "net", "deciduous", "commercial_caution", "Argentine NW trials"),
        _s("uy-montevideo", "Canelones", "UY", "UY-S", "Canelones", -34.72, -56.22, "nhb", "duke", "open_soil", "open", "none", "deciduous", "commercial_caution", "Uruguay hort"),
        _s("pt-odemira", "Odemira", "PT", "PT-ALEN", "Alentejo", 37.60, -8.64, "low_chill_shb", "biloxi", "substrate", "tunnel", "ldpe", "deciduous", "commercial_success", "Alentejo berries next to Huelva"),
        _s("pt-alcacer", "Alcácer do Sal", "PT", "PT-ALEN", "Alentejo", 38.37, -8.51, "low_chill_shb", "emerald", "substrate", "tunnel", "ldpe", "deciduous", "commercial_success", "Alentejo"),
        _s("us-nj-hammonton", "Hammonton", "US", "US-NE", "New Jersey", 39.64, -74.80, "nhb", "duke", "open_soil", "open", "none", "deciduous", "commercial_success", "Historic US blueberry, Atlantic County"),
        _s("us-nj-vineland", "Vineland", "US", "US-NE", "New Jersey", 39.49, -75.03, "nhb", "bluecrop", "open_soil", "open", "none", "deciduous", "commercial_success", "Cumberland"),
        _s("us-me-ellsworth", "Ellsworth", "US", "US-NE", "Maine", 44.54, -68.42, "nhb", "aurora", "open_soil", "open", "none", "deciduous", "commercial_success", "Wild + cultivated mix. Cultivated NHB only."),
        _s("us-ny-hudson", "Hudson Valley", "US", "US-NE", "New York", 42.25, -73.79, "nhb", "duke", "open_soil", "open", "none", "deciduous", "commercial_success", "NY hort"),
        _s("us-in-huntsville", "Southwest Michigan analog IN", "US", "US-MW", "Indiana", 41.68, -86.25, "nhb", "bluecrop", "open_soil", "open", "none", "deciduous", "commercial_caution", "Near Niles MI"),
        _s("cl-santiago", "Santiago basin", "CL", "CL-CENTRAL", "Metropolitana", -33.45, -70.67, "high_chill_shb", "legacy", "open_soil", "open", "none", "deciduous", "known_failure", "Too hot and dry for Legacy open field vs Osorno"),
        _s("pe-cusco", "Cusco highland", "PE", "PE-ANDES", "Cusco", -13.53, -71.97, "high_chill_shb", "legacy", "open_soil", "open", "none", "deciduous", "commercial_caution", "Andes. Hemp-class mountain data gap."),
        _s("us-tx-nacogdoches", "Nacogdoches", "US", "US-SE", "Texas", 31.60, -94.66, "rabbiteye", "brightwell", "open_soil", "open", "none", "deciduous", "commercial_success", "East Texas rabbiteye"),
        _s("us-la-hammond", "Hammond", "US", "US-SE", "Louisiana", 30.50, -90.46, "rabbiteye", "climax", "open_soil", "open", "none", "deciduous", "commercial_success", "Tangipahoa"),
        _s("us-ga-athens", "Athens GA", "US", "US-SE", "Georgia", 33.95, -83.38, "rabbiteye", "tifblue", "open_soil", "open", "none", "deciduous", "commercial_caution", "Piedmont, later and frostier than Alma"),
        _s("kr-hadong", "Hadong", "KR", "KR-S", "South Gyeongsang", 35.07, 127.75, "nhb", "duke", "open_soil", "open", "none", "deciduous", "commercial_caution", "Korea highland trials"),
        _s("jp-iwate", "Iwate", "JP", "JP-N", "Iwate", 39.70, 141.15, "nhb", "bluecrop", "open_soil", "open", "none", "deciduous", "commercial_caution", "Tohoku hort"),
        _s("th-chiang-mai", "Chiang Mai", "TH", "SEA", "Chiang Mai", 18.79, 98.99, "evergreen_zero_chill", "biloxi_evergreen", "substrate", "open", "net", "evergreen", "known_failure", "Low latitude, no winter DLI structure of Peru coast"),
        _s("eg-behira", "Beheira", "EG", "AF-N", "Beheira", 31.03, 30.47, "low_chill_shb", "biloxi", "substrate", "tunnel", "ldpe", "deciduous", "commercial_caution", "Nile Delta hort, fog/wet risk"),
        _s("tr-mersin", "Mersin", "TR", "TR-S", "Mersin", 36.80, 34.63, "low_chill_shb", "emerald", "open_soil", "tunnel", "ldpe", "deciduous", "commercial_caution", "East Med berry trials"),
        _s("gr-katerini", "Katerini", "GR", "EU-MED", "Central Macedonia", 40.27, 22.50, "nhb", "duke", "open_soil", "open", "none", "deciduous", "horticultural_absence", "Peach/kiwi hort, not blueberry"),
        _s("pl-lublin", "Lublin", "PL", "EU-CONT", "Lublin", 51.25, 22.57, "nhb", "duke", "open_soil", "open", "none", "deciduous", "commercial_caution", "Polish highbush, continental winter"),
        _s("de-hannover", "Hannover hinterland", "DE", "EU-CONT", "Lower Saxony", 52.37, 9.73, "nhb", "bluecrop", "open_soil", "open", "none", "deciduous", "commercial_caution", "German highbush"),
        _s("nl-venlo", "Venlo", "NL", "EU-ATL", "Limburg", 51.37, 6.17, "nhb", "duke", "substrate", "greenhouse", "none", "deciduous", "commercial_caution", "CEA, energy cost is the fingerprint"),
        _s("us-or-hood-river", "Hood River", "US", "US-PNW", "Oregon", 45.71, -121.52, "nhb", "draper", "open_soil", "open", "none", "deciduous", "commercial_caution", "Gorge wind and continental nights"),
        _s("us-wa-yakima", "Yakima", "US", "US-PNW", "Washington", 46.60, -120.51, "nhb", "duke", "open_soil", "open", "none", "deciduous", "commercial_caution", "East of Cascades. Not Whatcom."),
        _s("us-id-nampa", "Nampa", "US", "US-IW", "Idaho", 43.54, -116.56, "nhb", "bluecrop", "open_soil", "open", "none", "deciduous", "horticultural_absence", "Treasure Valley hort, not blueberry"),
        _s("mx-mexico-city", "Mexico City basin", "MX", "MX-CDMX", "Ciudad de México", 19.43, -99.13, "low_chill_shb", "biloxi", "open_soil", "open", "none", "deciduous", "horticultural_absence", "Urban highland, not Jalisco belt"),
        _s("br-vacaria", "Vacaria", "BR", "BR-S", "Rio Grande do Sul", -28.51, -50.94, "nhb", "duke", "open_soil", "open", "net", "deciduous", "commercial_success", "Brazilian highland blueberry"),
        _s("br-sao-joaquim", "São Joaquim", "BR", "BR-S", "Santa Catarina", -28.29, -49.93, "nhb", "bluecrop", "open_soil", "open", "net", "deciduous", "commercial_success", "Santa Catarina highland"),
        _s("co-bogota", "Bogotá savanna", "CO", "CO-ANDES", "Cundinamarca", 4.71, -74.07, "evergreen_zero_chill", "biloxi_evergreen", "substrate", "open", "net", "evergreen", "commercial_caution", "Equatorial highland. No analogue without gauges."),
        _s("ec-ambato", "Ambato", "EC", "EC-ANDES", "Tungurahua", -1.24, -78.63, "evergreen_zero_chill", "biloxi_evergreen", "substrate", "open", "net", "evergreen", "commercial_caution", "Andes data-trust flag"),
        _s("us-fl-miami", "Miami-Dade", "US", "US-SE", "Florida", 25.76, -80.19, "high_chill_shb", "star", "pine_bark", "open", "none", "deciduous", "known_failure", "No chill, no Star. Evergreen only further south."),
        _s("us-mi-marquette", "Marquette", "US", "US-MI", "Michigan", 46.54, -87.40, "nhb", "aurora", "open_soil", "open", "none", "deciduous", "known_failure", "UP winter too hard, season too short"),
    ]
)


COLUMNS = [
    "site_id",
    "name",
    "country",
    "region",
    "admin",
    "lat",
    "lon",
    "cultivar_class",
    "cultivar",
    "media",
    "structure",
    "cover",
    "habit",
    "outcome",
    "source",
    "geocode_precision",
    "notes",
]


def all_sites() -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for row in SITES:
        if row["site_id"] in seen:
            raise ValueError(f"Duplicate site_id {row['site_id']}")
        seen.add(row["site_id"])
        out.append(row)
    return out


def write_csv(path) -> int:
    import csv
    from pathlib import Path

    rows = all_sites()
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)