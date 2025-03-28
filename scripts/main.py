from pystorage.config import selectUnits, setTheScene, ureg
from pystorage.systems import DataDrivenElectricityStorageTechnology, ElectricityStorageTechnology
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

    setTheScene(country='UK', year=2015, warning=False, display=True)

    # Set the scene
    ES = ElectricityStorageTechnology().withInputs(
        dischargeDuration=Q_(5, 'hour'),
        dischargingPower=Q_(1000, 'MW'),
        chargingPower=Q_(1000, 'MW'),
        chargeDuration=Q_(6, 'hour'),
        powerIslandSpecificCost=Q_(500, 'USD/kW'),
        storeSpecificCost=Q_(10, 'USD/kWh'),
        selfDischargeRate=Q_(0.5, '%/hour'),
        cyclesPerYear=100,
        standby=0.,
        discountRate=Q_(3.5, '%'),
        lifetime=Q_(60, 'year'))

    ES.update(electricityPrice=Q_(79.68, 'USD/MWh'), gasPrice=Q_(31.27, 'USD/MWh'))
    LCOS = ES.levelisedCostOfStorage.to('USD/MWh')
    print(f'LCOS ()= {round(np.mean(LCOS).magnitude)} $/MWh')

    CAES = DataDrivenElectricityStorageTechnology().withInputs(
        dataSource='PNNL_CAES',
        dischargeDuration=Q_(4, 'hour'),
        dischargingPower=Q_(100, 'MW'),
        chargingPower=Q_(100, 'MW'),
        selfDischargeRate=Q_(0.5, '%/hour'),
        cyclesPerYear=100,
        standby=0.1,
        discountRate=Q_(3.5, '%'),
        lifetime=Q_(60, 'year'))

    CAES.update(electricityPrice=Q_(79.68, 'USD/MWh'), gasPrice=Q_(31.27, 'USD/MWh'))
    LCOS_1 = CAES.levelisedCostOfStorage.to('USD/MWh')
    print(f'LCOS = {round(np.mean(LCOS_1).magnitude)} $/MWh')

    CAES.update(electricityPrice=Q_(5, 'USD/MWh'), gasPrice=Q_(31.27, 'USD/MWh'))
    CAES.update(electricityPrice=Q_(79.68, 'USD/MWh'), gasPrice=Q_(31.27, 'USD/MWh'))
    LCOS_2 = CAES.levelisedCostOfStorage.to('USD/MWh')
    if not np.isclose(LCOS_1, LCOS_2).all():
        raise ValueError('Problem here!')

    setTheScene(country='UK', year=2024, warning=False, display=True)
    CAES.updateScene()
    LCOS = CAES.levelisedCostOfStorage.to('USD/MWh')
    print(f'LCOS = {round(np.mean(LCOS).magnitude)} $/MWh')
