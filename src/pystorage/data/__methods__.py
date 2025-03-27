from __future__ import annotations
from dataclasses import dataclass
import os
import pandas as pd
from ..config import ureg

""" Data classes """


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


""" Built-in methods """


def currencyIndex(currency):
    if currency == 'USD':
        return Currencies.USD
    elif currency == 'GBP':
        return Currencies.GBP
    elif currency == 'EUR':
        return Currencies.EUR
    else:
        return None


def extractAndResampleYearlyData(timeStep: float, year: int, country: str):

    """
      :param timeStep:                      data set time step [h]
      :param year:                          year [-]
      :param country:                       e.g., 'France'
    WARNING: Units used in this class are not SI units [e.g., Celsius, kWh, kW, h, £/kWh]
    """

    # Extract electricity tariffs
    if country == 'UK':

        df = pd.read_csv(os.path.dirname(os.path.abspath(__file__)) + '/electricityTariffs/' + country + '.csv',
                         sep=",| - ", engine='python')
        df['Time'] = pd.to_datetime(df['MTU (CET/CEST)'], format="%d.%m.%Y %H:%M")
        df = df[df['Time'].dt.strftime('%Y') == str(year)]
        if len(df) == 0:
            raise ValueError(f'Electricity tariff not available in {country} in {year}.')
        df['Time'] = df['Time']
        df = pd.Series(data=df['Day-ahead Price [GBP/MWh]'].values, index=df['Time'].values)
        idx = df.tail(1).index[0] + (df.index[1] - df.index[0])
        df.loc[idx] = df.iloc[-1]
        df = df[~df.index.duplicated(keep='first')]
        upSampled = df.resample("".join([str(timeStep), 'h']))
        electricityTariff = upSampled.interpolate(method='linear')

        unit = 'GBP/MWh'

    else:

        df = pd.read_csv(os.path.dirname(os.path.abspath(__file__)) + '/electricityTariffs/' + country + '.csv')
        df['Datetime (UTC)'] = pd.to_datetime(df['Datetime (UTC)'])
        df = df[df['Datetime (UTC)'].dt.strftime('%Y') == str(year)]
        if len(df) == 0:
            raise ValueError(f'Electricity tariff not available in {country} in {year}.')
        df['Time'] = df['Datetime (UTC)']
        electricityTariff = pd.Series(data=df['Price (EUR/MWhe)'].values, index=df['Datetime (UTC)'].values)
        idx = electricityTariff.tail(1).index[0] + (df['Time'].iloc[1] - df['Time'].iloc[0])
        electricityTariff.loc[idx] = electricityTariff.iloc[-1]
        upSampled = electricityTariff.resample("".join([str(timeStep), 'h']))
        electricityTariff = upSampled.interpolate(method='linear')

        unit = 'EUR/MWh'

    return electricityTariff, unit


""" Data structures """

# Chemical Engineering Plant Cost Index
fileDirectory = os.path.dirname(os.path.realpath(__file__))
CEPCI = pd.read_csv(filepath_or_buffer=fileDirectory + '/CEPCI/CEPCI.csv',
                    index_col=0,
                    header=None).squeeze('columns')

# Compressed Air Electricity Storage (CAES) data from PNNL
data = pd.read_csv(filepath_or_buffer=fileDirectory + '/CAES/PNNL.csv', header=[0, 1])
PNNL_CAES = {}
for field, unit in data.columns:
    PNNL_CAES[field] = [float(x[0]) for x in data[field].values] * ureg[unit]

# Gather currency data in a _Currencies object
_currencyData = pd.read_csv(filepath_or_buffer=fileDirectory + '/Currencies/Currencies.csv', header=0)
Currencies = _Currencies(USD=float(_currencyData.USD.values[0]),
                         GBP=float(_currencyData.GBP.values[0]),
                         EUR=float(_currencyData.EUR.values[0]))