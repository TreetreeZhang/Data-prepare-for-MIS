from decimal import Decimal
from typing import List


def compute_scale_factor(values: List[float]) -> int:
    max_places = 0
    for value in values:
        dec = Decimal(str(value)).normalize()
        places = -dec.as_tuple().exponent if dec.as_tuple().exponent < 0 else 0
        if places > max_places:
            max_places = places
    return 10 ** max_places

