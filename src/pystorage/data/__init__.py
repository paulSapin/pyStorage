from __future__ import annotations
from dataclasses import dataclass
import os
import pandas as pd


# Dataclass definitions
@dataclass
class _Currencies:
    USD: float
    GBP: float
    EUR: float


@dataclass
class _EnergyPrice:
    electricity: float
    gas: float
    hydrogen: float


# Chemical Engineering Plant Cost Index
fileDirectory = os.path.dirname(os.path.realpath(__file__))
CEPCI = pd.read_csv(filepath_or_buffer=fileDirectory + '/CEPCI.csv',
                    index_col=0,
                    header=None).squeeze('columns')

# Compressed Air Electricity Storage (CAES) data from PNNL
PNNL_CAES = pd.read_csv(filepath_or_buffer=fileDirectory + '/PNNL_CAES.csv', header=0)

# Gather currency data in a _Currencies object
_currencyData = pd.read_csv(filepath_or_buffer=fileDirectory + '/Currencies.csv', header=0)
Currencies = _Currencies(USD=float(_currencyData.USD.values[0]),
                         GBP=float(_currencyData.GBP.values[0]),
                         EUR=float(_currencyData.EUR.values[0]))


def currencyIndex(currency):
    if currency == 'USD':
        return Currencies.USD
    elif currency == 'GBP':
        return Currencies.GBP
    elif currency == 'EUR':
        return Currencies.EUR
    else:
        return None


# Gather currency data in a _EnergyPrice object
EnergyPrices_UK = _EnergyPrice(  # OFGEM 2024
    electricity=79.68 * Currencies.USD / Currencies.GBP,  # USD/MWh
    gas=31.27 * Currencies.USD / Currencies.GBP,  # USD/MWh
    hydrogen=79.68 * Currencies.USD / Currencies.GBP  # USD/MWh
)
