from __future__ import annotations
from dataclasses import dataclass
import os
import pandas as pd

# Chemical Engineering Plant Cost Index
fileDirectory = os.path.dirname(os.path.realpath(__file__))
CEPCI = pd.read_csv(filepath_or_buffer=fileDirectory + '/CEPCI.csv',
                    index_col=0,
                    header=None).squeeze('columns')


@dataclass
class Currencies:
    USD = 1
    GBP = 0.77
    EUR = 0.92


@dataclass
class _EnergyPrice:
    electricity: float | None
    gas: float | None
    hydrogen: float | None


EnergyPrices_UK = _EnergyPrice(  # OFGEM 2024
    electricity=79.68 * Currencies.USD / Currencies.GBP,  # USD/MWh
    gas=31.27 * Currencies.USD / Currencies.GBP,  # USD/MWh
    hydrogen=79.68 * Currencies.USD / Currencies.GBP  # USD/MWh
)
