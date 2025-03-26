import pystorage as pyes
from rich import print
import os
import pwd
import sys

if pyes.config.Currency is None:
    pyes.config.selectCurrency('USD')


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


if __name__ == '__main__':

    print(hello(user=pwd.getpwuid(os.getuid())[0]))

    """ Set the scene """
    pyes.config.setTheScene(country='UK', year=2024)
    CAES_UK = pyes.technologies.powerToPower.DataDrivenElectricityStorageTechnology().withInputs(dataSource='PNNL_CAES')

    """ Change the scene """
    pyes.config.setTheScene(country='France', year=2024)
    CAES_FR = pyes.technologies.powerToPower.DataDrivenElectricityStorageTechnology().withInputs(dataSource='PNNL_CAES')

    # # Systems specs
    # dt = 4  # h
    # power = 100  # MW
    # selfDischargeRate = 0  # %/day
    # frequency = 100.
    # standby = 0.
    # discountRate = 0.035
    # lifetime = 60
    #
    # # Digital twin based on DataDrivenElectricityStorageTechnology
    # CAES = pyes.technologies.powerToPower.DataDrivenElectricityStorageTechnology().withInputs(
    #     dataSource='PNNL_CAES',
    #     dischargeDuration=dt * 3600,  # seconds
    #     dischargingPower=power * 1e6,  # W
    #     chargingPower=power * 1e6,  # W
    #     selfDischargeRate=selfDischargeRate,  # %/h
    #     frequency=frequency,
    #     standby=standby,
    #     discountRate=discountRate,
    #     lifetime=lifetime)
    #
    # CAES.updateEnergyPrices(currency='GBP', electricity=79.68, gas=31.27)
