from pystorage.config import selectUnits, setTheScene, ureg, getTheScene, getUnits
from pystorage.systems import DataDrivenElectricityStorageTechnology, ElectricityStorageTechnology

Q_ = ureg.Quantity
setTheScene(country='UK', year=2024, warning=False, display=True)


# Test set country and year
def test_setup():

    scene = getTheScene()
    ES = DataDrivenElectricityStorageTechnology().withInputs(dataSource='PNNL_CAES')

    assert ES.year == int(scene['Year'])


# Test creation of a conventional CAES object
def test_CAES_DataDriven():

    ES = DataDrivenElectricityStorageTechnology().withInputs(dataSource='PNNL_CAES')

    assert (ES.type == 'D-CAES' and ES.secondarySource == 'gas' and ES.model == 'PNNL')


# Test creation of a technology-agnostic ES object with a specific design
def test_Agnostic_ES():

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

    assert ES.nominalDischargeDuration / ES.nominalChargeDuration == ES.nominalRoundTripEfficiency


# Test creation of a conventional CAES object with a specific design
def test_CAES_DataDrivenDesign():

    ES = DataDrivenElectricityStorageTechnology().withInputs(
        dataSource='PNNL_CAES',
        dischargeDuration=Q_(4, 'hour'),
        dischargingPower=Q_(100, 'MW'),
        chargingPower=Q_(100, 'MW'),
        selfDischargeRate=Q_(0.5, '%/hour'),
        cyclesPerYear=100,
        standby=0.1,
        discountRate=Q_(3.5, '%'),
        lifetime=Q_(60, 'year'))

    assert ES.nominalDischargeDuration / ES.nominalChargeDuration == ES.nominalRoundTripEfficiency


# Test LCOS calculation conventional CAES objects
def test_LCOS_DataDriven():

    ES = DataDrivenElectricityStorageTechnology().withInputs(
        dataSource='PNNL_CAES',
        dischargeDuration=Q_(4, 'hour'),
        dischargingPower=Q_(100, 'MW'),
        chargingPower=Q_(100, 'MW'),
        selfDischargeRate=Q_(0.5, '%/hour'),
        cyclesPerYear=100,
        standby=0.1,
        discountRate=Q_(3.5, '%'),
        lifetime=Q_(60, 'year'))

    ES.update(electricityPrice=Q_(79.68, 'USD/MWh'), gasPrice=Q_(31.27, 'USD/MWh'))
    LCOS = ES.levelisedCostOfStorage.to('USD/MWh').magnitude

    assert LCOS is not None and len(LCOS) == 3
