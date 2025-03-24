from rich import print
from sys import version_info as vi
from sys import modules

python_version = f"Python {vi.major}.{vi.minor}"

""" Add a global variable for the country and year """
this = modules[__name__]  # this is a pointer to the module object instance itself.
this.country = None
this.year = None


def initialize(country, year):

    if this.country is None:  # also in local function scope. no scope specifier like global is needed
        this.country = country
    else:
        msg = "Country is already set to {0}."
        raise RuntimeError(msg.format(this.country))

    if this.year is None:  # also in local function scope. no scope specifier like global is needed
        this.year = year
    else:
        msg = "Year is already set to {0}."
        raise RuntimeError(msg.format(this.year))


def hello():

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

    return message


def say_hello():

    print(hello())

