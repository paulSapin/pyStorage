Year = None
Currency = None
Country = None


def defineAdditionalUnits():

    import pint
    import os

    fileDirectory = os.path.dirname(os.path.realpath(__file__))
    UnitRegistry = pint.UnitRegistry()
    UnitRegistry.load_definitions(fileDirectory + '/currencyConversionRates.txt')

    return UnitRegistry


def selectUnits(*,
                currency: str = 'USD',
                time: str = 'hour',
                power: str = 'kW',
                energy: str = 'kWh',
                efficiency: str = '%',
                ):

    import csv
    import os

    fileDirectory = os.path.dirname(os.path.realpath(__file__))

    units = {"currency": currency,
             'time': time,
             'power': power,
             'energy': energy,
             'efficiency': efficiency,
             'energySpecificCost': currency + '/' + energy,
             'powerSpecificCost': currency + '/' + power}

    with open(fileDirectory + "/units.csv", "w", newline="") as f:
        w = csv.DictWriter(f, units.keys())
        w.writeheader()
        w.writerow(units)


def setTheScene(*, country=None, year=None, warning=True):

    import warnings
    import csv
    import os

    fileDirectory = os.path.dirname(os.path.realpath(__file__))

    global Currency
    global Country
    global Year

    if country is not None:

        if not isinstance(country, str):
            raise TypeError('The input variable "country" must be a string.')

        if Country is None:
            Country = country
        else:
            if Country != country and warning:
                msg = (f"Country is already set to {Country}. " +
                       f"Changing to {country} will only affect newly created objects.")
                warnings.warn(msg)
            Country = country

    if year is not None:

        if not isinstance(year, int):
            raise TypeError('The input variable "year" must be a positive integer.')

        if Year is None:
            Year = year
        else:
            if Year != year and warning:
                msg = (f"Year is already set to {Year}. " +
                       f"Changing to {year} will only affect newly created objects.")
                warnings.warn(msg)
            Year = year

    scene = {"Country": Country, "Year": Year}

    with open(fileDirectory + "/__scene__.csv", "w", newline="") as f:
        w = csv.DictWriter(f, scene.keys())
        w.writeheader()
        w.writerow(scene)


def getTheScene():

    import os
    import csv

    fileDirectory = os.path.dirname(os.path.realpath(__file__))

    if '__scene__.csv' not in os.listdir(fileDirectory):
        raise NotImplementedError('Country & year must be set ' +
                                  'to perform a techno-economic analysis. \n' +
                                  'Please use pystorage.config.setTheScene() function in your main script.')
    else:  # Get the scene
        mydict = csv.DictReader(open(fileDirectory + '/__scene__.csv'))
        mydict = [row for row in mydict]
        scene = mydict[0]

    return scene


def getUnits():

    import os
    import csv

    fileDirectory = os.path.dirname(os.path.realpath(__file__))

    if 'units.csv' not in os.listdir(fileDirectory):
        raise NotImplementedError('Units (including currency) must be set ' +
                                  'to perform a techno-economic analysis. \n' +
                                  'Please use pystorage.config.selectUnits() function in your main script.')
    else:  # Get the scene
        mydict = csv.DictReader(open(fileDirectory + '/units.csv'))
        mydict = [row for row in mydict]
        units = mydict[0]

    return units


# Select default units
selectUnits()

# Define unit registry
ureg = defineAdditionalUnits()
