"""Small shared statistical helpers used across the analytics services."""
import math


def normal_sf_two_sided(z):
    """Two-sided survival function of the standard normal — the p-value for a
    z-statistic. Shared by the Cox and mixed-model fits."""
    return math.erfc(abs(z) / math.sqrt(2.0))
