from __future__ import annotations
from .systems import *
from .components import *
from .thermophysicalProperties import *
import warnings
import sys

""" Add global variables and set function """

Year: int | None = None
Currency: str | None = None
Country: str | None = None


def setTheScene(*,
                country: str | None = None,
                year: int | None = None,
                currency: str | None = None,
                noWarning: bool = False):
    global Country
    global Year
    global Currency

    if country is not None:
        if Country is None:
            Country = country
        else:
            if not noWarning:
                msg = (f"Country is already set to {Country}. " +
                       f"Changing to {country} will only affect newly created objects.")
                warnings.warn(msg)
            Country = country

    if year is not None:
        if Year is None:
            Year = year
        else:
            if not noWarning:
                msg = (f"Year is already set to {Year}. " +
                       f"Changing to {year} will only affect newly created objects.")
                warnings.warn(msg)
                Year = year

    if currency is not None:
        if Currency is None:
            Currency = currency
        else:
            msg = "Currency is already set to {0}."
            raise RuntimeError(msg.format(Currency))


def hello(user):
    python_version = f"Python {sys.version_info.major}.{sys.version_info.minor}"

    # ASCII art font generated with https://patorjk.com/software/taag/

    message = rf"""
    
        [green]
         ____   _  _   ____   ____    __    ____    __     ___   ____
        (  _ \ ( \/ ) / ___) (_  _)  /  \  (  _ \  / _\   / __) (____)
         ) __/  )  /  \___ \   )(   ( O  )  )   / /    \ ( (_ \  ) _) 
        (__)   (__/   (____/  (__)   \__/  (__\_) \_/\_/  \___/ (____)
        [/green]

        Hello {user},

        Currently running pyStorage with {python_version}

        Multi-fidelity electricity storage modelling framework
        Technology-agnostic, data-driven \u0026 comprehensive first-law models
        Design \u0026 dispatch optimisation

        Available in open-source Github repository: 
        https://github.com/paulSapin/pyStorage

        For more information, contact Dr Paul Sapin at p.sapin@imperial.ac.uk

        """

    return message
