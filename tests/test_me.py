from pystorage.systems import powerToPower
from pystorage.tools import math
from pystorage.data import EnergyPrices_UK
from pystorage import *
from sys import version_info as vi
import pystorage

python_version = f"Python {vi.major}.{vi.minor}"


# Test hello function in pystorage.__init__.py
def test_hello():

    message = f"""
        [bold red]pyStorage[/bold red]

        Currently running with {python_version}

        Multi-fidelity electricity storage modelling framework
        Technology-agnostic, data-driven \u0026 comprehensive first-law models
        Design \u0026 dispatch optimisation

        Available in open-source Github repository: 
        https://github.com/paulSapin/pyStorage

        For more information, contact Dr Paul Sapin at p.sapin@imperial.ac.uk
        """

    assert hello() == message


# Test set country and year
def test_setup():
    initialize(country='UK', year=2024)
    assert pystorage.country == 'UK' and pystorage.year == 2024


# Test data collection in pystorage.__init__()
def test_data():

    # Collect data
    electricityPrice = EnergyPrices_UK.electricity
    gasPrice = EnergyPrices_UK.gas
    hydrogenPrice = EnergyPrices_UK.hydrogen

    assert (isinstance(electricityPrice, float) and
            isinstance(gasPrice, float) and
            isinstance(hydrogenPrice, float))


# Test creation of a conventional CAES object
def test_ConventionalCAES():

    ES = powerToPower.ConventionalCAES()

    assert (ES.type == 'D-CAES' and ES.secondarySource[0] == 'gas' and ES.model == 'PNNL')


# Test creation of a conventional CAES object with a specific design
def test_DesignConventionalCAES():

    dt = 12  # h
    power = 100  # MW
    selfDischargeRate = 5  # %/day
    ES = powerToPower.ConventionalCAES().withInputs(
        dischargeDuration=dt * 3600,  # seconds
        dischargingPower=power * 1e6,  # W
        chargingPower=power * 1e6,  # W
        selfDischargeRate=math.convertRate(selfDischargeRate, 1 / 24)  # %/h
    )

    assert dt / ES.nominalChargeDuration_hours == ES.nominalRoundTripEfficiency


# Test design methods of conventional CAES objects
def test_DesignMethodsConventionalCAES():

    dt = 12  # h
    power = 100  # MW
    selfDischargeRate = 5  # %/day
    ES = powerToPower.ConventionalCAES().withInputs(
        dischargeDuration=dt * 3600,  # seconds
        dischargingPower=power * 1e6,  # W
        chargingPower=power * 1e6,  # W
        selfDischargeRate=math.convertRate(selfDischargeRate, 1 / 24),  # %/h
        lifetime=60
    )

    ES_twin = powerToPower.ConventionalCAES()
    ES_twin.defineDesign(
        dischargeDuration=dt * 3600,  # seconds
        dischargingPower=power * 1e6,  # W
        chargingPower=power * 1e6,  # W
        selfDischargeRate=math.convertRate(selfDischargeRate, 1 / 24),  # %/h
        lifetime=60
    )

    assert all(x == y for (x, y) in zip(ES.powerIslandSpecificCost_per_kW, ES_twin.powerIslandSpecificCost_per_kW))


# Test conventional CAES OCs
def test_OperatingConditionsConventionalCAES():

    dt = 12  # h
    power = 100  # MW
    selfDischargeRate = 5  # %/day
    ES = powerToPower.ConventionalCAES().withInputs(
        dischargeDuration=dt * 3600,  # seconds
        dischargingPower=power * 1e6,  # W
        chargingPower=power * 1e6,  # W
        selfDischargeRate=math.convertRate(selfDischargeRate, 1 / 24)  # %/h
    )

    ES.defineOperatingConditions(frequency=100, standby=0.)

    assert ES.roundtripEfficiency == ES.nominalRoundTripEfficiency


# Test lifetime cost calculation
def test_LCOS_ConventionalCAES():

    dt = 12  # h
    power = 100  # MW
    selfDischargeRate = 5  # %/day
    ES = powerToPower.ConventionalCAES().withInputs(
        dischargeDuration=dt * 3600,  # seconds
        dischargingPower=power * 1e6,  # W
        chargingPower=power * 1e6,  # W
        selfDischargeRate=math.convertRate(selfDischargeRate, 1 / 24),  # %/h
        lifetime=60
    )

    ES.defineOperatingConditions(frequency=100, standby=0.)
    ES.updateDiscountRate(discountRate=0.035)
    ES.updateEnergyPrices(electricity=EnergyPrices_UK.electricity, gas=EnergyPrices_UK.gas)

    assert all([x > 0 for x in ES.levelisedCostOfStorage])
