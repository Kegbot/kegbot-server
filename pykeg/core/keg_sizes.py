"""Constants about physical keg shell."""

# Most common shell sizes, from smalles to largest.
MINI = "mini"
CORNY_25 = "corny-2_5-gal"
CORNY_30 = "corny-3-gal"
CORNY = "corny"
SIXTH_BARREL = "sixth"
EURO_30_LITER = "euro-30-liter"
EURO_HALF_BARREL = "euro-half"
QUARTER_BARREL = "quarter"
EURO = "euro"
HALF_BARREL = "half-barrel"
OTHER = "other"

VOLUMES_ML = {
    MINI: 5000,
    CORNY_25: 9463.53,
    CORNY_30: 11356.2,
    CORNY: 18927.1,
    SIXTH_BARREL: 19570.6,
    EURO_30_LITER: 300000.0,
    EURO_HALF_BARREL: 50000.0,
    QUARTER_BARREL: 29336.9,
    EURO: 100000.0,
    HALF_BARREL: 58673.9,
    OTHER: 0.0,
}

DESCRIPTIONS = {
    MINI: "Mini Keg (5 L)",
    CORNY_25: "Corny Keg (2.5 gal)",
    CORNY_30: "Corny Keg (3.0 gal)",
    CORNY: "Corny Keg (5 gal)",
    SIXTH_BARREL: "Sixth Barrel (5.17 gal)",
    EURO_30_LITER: "European DIN (30 L)",
    EURO_HALF_BARREL: "European Half Barrel (50 L)",
    QUARTER_BARREL: "Quarter Barrel (7.75 gal)",
    EURO: "European Full Barrel (100 L)",
    HALF_BARREL: "Half Barrel (15.5 gal)",
    OTHER: "Other",
}

CHOICES = [(x, DESCRIPTIONS[x]) for x in reversed(sorted(VOLUMES_ML, key=VOLUMES_ML.get))]


def find_closest_keg_size(volume_ml, tolerance_ml=100.0):
    """Returns the nearest fuzzy match name within tolerance_ml.

    If no match is found, OTHER is returned.
    """
    for size_name, size_volume_ml in list(VOLUMES_ML.items()):
        diff = abs(volume_ml - size_volume_ml)
        if diff <= tolerance_ml:
            return size_name
    return OTHER


def get_description(keg_type):
    return DESCRIPTIONS.get(keg_type, "Unknown")
