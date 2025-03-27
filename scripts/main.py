from pystorage.config import selectUnits, setTheScene, ureg
from pystorage.systems import DataDrivenElectricityStorageTechnology
from rich import print
import numpy as np
import os
import pwd
import sys

selectUnits(currency='USD')
Q_ = ureg.Quantity


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
        Technology-agnostic, data-driven & comprehensive first-law models
        Design & dispatch optimisation

        Available in open-source Github repository: 
        https://github.com/paulSapin/pyStorage

        For more information, contact Dr Paul Sapin at p.sapin@imperial.ac.uk

        """

    return message


if __name__ == '__main__':

    print(hello(user=pwd.getpwuid(os.getuid())[0]))

    # Set the scene
    setTheScene(country='France', year=2024, warning=False)

    # CAES DataDrivenElectricityStorageTechnology
    CAES = DataDrivenElectricityStorageTechnology().withInputs(
        dataSource='PNNL_CAES',
        dischargeDuration=Q_(4, 'hour'),
        dischargingPower=Q_(100, 'MW'),
        chargingPower=Q_(100, 'MW'),
        selfDischargeRate=Q_(100, '%/hour'),
        frequency=Q_(100, '1/year'),
        standby=0,
        discountRate=Q_(100, '%'),
        lifetime=Q_(60, 'year'))

    # CAES.updateEnergyPrices(currency='GBP', electricity=79.68, gas=31.27)
    #
    # LCOS1 = CAES.levelisedCostOfStorage
    #
    # setTheScene(country='France', year=2000, warning=False)
    # CAES.updateScene()
    #
    # setTheScene(country='France', year=2024, warning=False)
    # CAES.updateScene()
    #
    # LCOS2 = CAES.levelisedCostOfStorage
    #
    # if not np.isclose(LCOS1, LCOS2).all():
    #     raise ValueError('Problem here!')
    #
    # x: ureg.Quantity | None = None
