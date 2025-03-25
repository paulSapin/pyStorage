import pystorage as pyes
from rich import print
from sys import version_info as vi

pyes.setScene(country='UK', year=2025, currency='GBP')


def hello():

    python_version = f"Python {vi.major}.{vi.minor}"

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


if __name__ == '__main__':

    print(hello())

    CAES = pyes.systems.powerToPower.DataDrivenElectricityStorageTechnology().withInputs(dataSource='PNNL_CAES')
