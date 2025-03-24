import numpy as np


def convertRate(rate, outputInputRatio):
    # EG: r[%/hour] = - 100 / [24 hours in a day] * ln(1 - r[%/day] / 100)
    return - 100 * outputInputRatio * np.log(1 - rate / 100)
