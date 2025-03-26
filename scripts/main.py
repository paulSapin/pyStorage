import pystorage as pyes
from rich import print
import os
import pwd

""" SET SCENE """
if pyes.Currency is None:
    pyes.setTheScene(country='UK', year=2024, currency='GBP')


if __name__ == '__main__':

    print(pyes.hello(user=pwd.getpwuid(os.getuid())[0]))

    # Systems specs
    dt = 4  # h
    power = 100  # MW
    selfDischargeRate = 0  # %/day
    frequency = 100.
    standby = 0.
    discountRate = 0.035
    lifetime = 60

    # Digital twin based on DataDrivenElectricityStorageTechnology
    CAES = pyes.powerToPower.DataDrivenElectricityStorageTechnology().withInputs(
        dataSource='PNNL_CAES',
        dischargeDuration=dt * 3600,  # seconds
        dischargingPower=power * 1e6,  # W
        chargingPower=power * 1e6,  # W
        selfDischargeRate=selfDischargeRate,  # %/h
        frequency=frequency,
        standby=standby,
        discountRate=discountRate,
        lifetime=lifetime)

    CAES.updateEnergyPrices(currency='GBP', electricity=79.68, gas=31.27)
