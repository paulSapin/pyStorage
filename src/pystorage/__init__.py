from __future__ import annotations
from .systems import *
from .components import *
from .thermophysicalProperties import *

""" Add global variables and set function """

Year: int | None = None
Currency: str | None = None
Country: str | None = None


def setScene(country: str, year: int, currency: str):

    global Country
    global Year
    global Currency

    if Country is None:
        Country = country
    else:
        msg = "Country is already set to {0}."
        raise RuntimeError(msg.format(Country))

    if Year is None:
        Year = year
    else:
        msg = "Year is already set to {0}."
        raise RuntimeError(msg.format(Year))

    if Currency is None:
        Currency = currency
    else:
        msg = "Currency is already set to {0}."
        raise RuntimeError(msg.format(Currency))

