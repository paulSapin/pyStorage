from pystorage.config import selectUnits, setTheScene, getUnits, ureg
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
        Default currency: {getUnits()['currency']} (can be changed with pystorage.config.selectUnits)

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

    # TODO: Check currency conversion works...not there yet!

    selectUnits(currency='GBP')

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
    LCOS_1 = CAES.levelisedCostOfStorage.to('GBP/MWh', 'conversion')
    print(f'LCOS = {round(np.mean(LCOS_1).magnitude)} £/MWh')
