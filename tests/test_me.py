from pystorage.systems import powerToPower
from pystorage.tools import math
from scipy.interpolate import LinearNDInterpolator
from pystorage.data import CEPCI, PNNL_CAES, currencyIndex
from pystorage import *

print('Running tests.')


# Test set country and year
def test_setup():

    setTheScene(country='UK', year=2024, currency='GBP')
    ES = powerToPower.DataDrivenElectricityStorageTechnology().withInputs(dataSource='PNNL_CAES')

    assert ES.year == pystorage.Year


# Test creation of a conventional CAES object
def test_CAES_DataDriven():

    ES = powerToPower.DataDrivenElectricityStorageTechnology().withInputs(dataSource='PNNL_CAES')

    assert (ES.type == 'D-CAES' and ES.secondarySource[0] == 'gas' and ES.model == 'PNNL')


# Test creation of a conventional CAES object with a specific design
def test_Design_DataDriven():

    dt = 12  # h
    power = 100  # MW
    selfDischargeRate = 5  # %/day
    ES = powerToPower.DataDrivenElectricityStorageTechnology().withInputs(
        dataSource='PNNL_CAES',
        dischargeDuration=dt * 3600,  # seconds
        dischargingPower=power * 1e6,  # W
        chargingPower=power * 1e6,  # W
        selfDischargeRate=math.convertRate(selfDischargeRate, 1 / 24)  # %/h
    )

    assert dt / ES.nominalChargeDuration_hours == ES.nominalRoundTripEfficiency


# Test design methods of conventional CAES objects
def test_DesignMethods_DataDriven():

    dt = 12  # h
    power = 100  # MW
    selfDischargeRate = 5  # %/day
    ES = powerToPower.DataDrivenElectricityStorageTechnology().withInputs(
        dataSource='PNNL_CAES',
        dischargeDuration=dt * 3600,  # seconds
        dischargingPower=power * 1e6,  # W
        chargingPower=power * 1e6,  # W
        selfDischargeRate=math.convertRate(selfDischargeRate, 1 / 24),  # %/h
        lifetime=60
    )

    ES_twin = powerToPower.DataDrivenElectricityStorageTechnology().withInputs(dataSource='PNNL_CAES')
    ES_twin.updateDesign(
        dischargeDuration=dt * 3600,  # seconds
        dischargingPower=power * 1e6,  # W
        chargingPower=power * 1e6,  # W
        selfDischargeRate=math.convertRate(selfDischargeRate, 1 / 24),  # %/h
        lifetime=60
    )

    assert all(x == y for (x, y) in zip(ES.powerIslandSpecificCost_per_kW, ES_twin.powerIslandSpecificCost_per_kW))


# Test PNNL database
def test_PNNL_database():

    """
    Check manual input into ElectricityStorageTechnology VS DataDrivenElectricityStorageTechnology pointing to map

    # PNNL performance metrics
    exergyEfficiency = 0.52  # Wout / (Win + Wg)
    carnotEfficiency = 0.49  # Wg / Qg
    roundtripEfficiency = 0.746  # Wout / Win

    # Gas consumption ratio upon discharge [kWh_g / kWh_e]
    gasConsumptionRatio = 1 / carnotEfficiency * (1 / exergyEfficiency - 1 / roundtripEfficiency)  # = Qg / Wout

    """

    # Conversion factor
    dataCurrencyIndex = currencyIndex('USD')
    systemCurrencyIndex = currencyIndex(pystorage.Currency)
    k = systemCurrencyIndex / dataCurrencyIndex

    # Extract data
    duration = PNNL_CAES.duration.values
    power = PNNL_CAES.power.values
    roundtripEfficiency = PNNL_CAES.roundtripEfficiency.values
    secondaryConsumptionRatio = PNNL_CAES.secondaryConsumptionRatio.values
    powerIslandSpecificCost = PNNL_CAES.powerIslandSpecificCost.values * k
    storeSpecificCost = PNNL_CAES.storeSpecificCost.values * k

    # Scattered interpolation for technical performance
    roundtripEfficiency_int = LinearNDInterpolator(list(zip(duration, power)), roundtripEfficiency)
    secConsumptionRatio_int = LinearNDInterpolator(list(zip(duration, power)), secondaryConsumptionRatio)

    # Scattered interpolation for power island SIC
    powerIslandSIC = LinearNDInterpolator(list(zip(duration, power)), powerIslandSpecificCost)

    # Scattered interpolation for store SIC
    saltCavernSIC = LinearNDInterpolator(list(zip(duration, power)), storeSpecificCost)

    # Systems specs
    dt = 4  # h
    power = 1000  # MW
    selfDischargeRate = 0  # %/day
    frequency = 100.
    standby = 0.
    discountRate = 0.035
    lifetime = 60

    # Interpolate data
    roundtripEfficiency = roundtripEfficiency_int(dt, power)
    gasConsumptionRatio = secConsumptionRatio_int(dt, power)
    powerIslandSpecificCost = powerIslandSIC(dt, power) * (CEPCI[pystorage.Year] / CEPCI[2023])
    storeSpecificCost = saltCavernSIC(dt, power) * (CEPCI[pystorage.Year] / CEPCI[2023])

    # Construct the first object
    CAES = powerToPower.ElectricityStorageTechnology().withInputs(
        dischargeDuration=dt * 3600,  # seconds
        dischargingPower=power * 1e6,  # W
        chargingPower=power * 1e6,  # W
        roundtripEfficiency=roundtripEfficiency,
        secondarySource='gas',
        secondaryConsumptionRatio=gasConsumptionRatio,
        selfDischargeRate=selfDischargeRate,  # %/h
        frequency=frequency,
        standby=standby,
        discountRate=discountRate,
        lifetime=lifetime,
        powerIslandSpecificCost=powerIslandSpecificCost,
        storeSpecificCost=storeSpecificCost)

    CAES.updateEnergyPrices(currency='GBP', electricity=79.68, gas=31.27)

    # Digital twin based on DataDrivenElectricityStorageTechnology
    CAES_twin = powerToPower.DataDrivenElectricityStorageTechnology().withInputs(
        dataSource='PNNL_CAES',
        dischargeDuration=dt * 3600,  # seconds
        dischargingPower=power * 1e6,  # W
        chargingPower=power * 1e6,  # W
        selfDischargeRate=selfDischargeRate,  # %/h
        frequency=frequency,
        standby=standby,
        discountRate=discountRate,
        lifetime=lifetime)

    CAES_twin.updateEnergyPrices(currency='GBP', electricity=79.68, gas=31.27)

    assert np.isclose(CAES.levelisedCostOfStorage, CAES_twin.levelisedCostOfStorage[1])
