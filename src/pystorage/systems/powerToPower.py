from __future__ import annotations

from scipy.interpolate import LinearNDInterpolator
import numpy as np
from abc import ABC, abstractmethod
from pystorage.data import CEPCI

""" ABSTRACT CLASS """


class AbstractElectricityStorageTechnology(ABC):

    @abstractmethod
    def __init__(self):

        # Battery type
        self._type: str | None = None  #                        PHES/LAES/(A-D-I-)CAES/PTES/Flow/LiIon/Flywheel

        # Battery technical characteristics (size)
        self._dischargeDuration: float | None = None  #         Discharge duration                  [s]
        self._dischargingPower: float | None = None  #          Discharging rate/power              [W]
        self._chargeDuration: float | None = None  #            Charge duration                     [s]
        self._chargingPower: float | None = None  #             Charging rate/power                 [W]

        # Battery technical performance
        self._roundtripEfficiency: float | None = None  #       Elec-to-elec roundtrip efficiency   > 0
        self._selfDischargeRate: float | None = None  #         Self-discharge rate                 [0 - 1]

        # Secondary fuel / energy vector
        self._secSource: str | None = None  #                   Secondary energy source             (e.g., gas, H2)
        self._secConsumptionRatio: float | None = None  #       Consumption ratio upon discharge    [kWh_g / kWh_e]

        # Battery economic value
        self._powerIslandSpecificCost: float | None = None  #   Power island specific cost          [$/kW]
        self._storeSpecificCost: float | None = None  #         Energy store specific cost          [$/kWh]

        # Currency
        self._currency: str | None = None  #                    Currency                            [USD, GBP, EUR]

        # Economic conditions (scenario- & country-dependent parameters)
        self._electricityPrice: float | None = None  #          Electricity tariff                  [$/MWh]
        self._gasPrice: float | None = None  #                  Gas price                           [$/MWh]
        self._hydrogenPrice: float | None = None  #             Hydrogen price                      [$/MWh]
        self._discountRate: float | None = None  #              Discount rate                       [0 - 1]

        # Utilisation / operational parameters
        self._lifetime: int | None = None  #                    System lifetime                     [years]
        self._frequency: int | None = None  #                   Number of cycles / year             [1 - maxFreq]
        self._standby: float | None = None  #                   Non-dimensional standby duration    [0 - 1]

        # Ghost dependent properties
        self.__workingCycleDuration: float | None = None
        self.__wholeCycleDuration: float | None = None
        self.__standbyDuration: float | None = None
        self.__maximumFrequency: float | None = None
        self.__investmentCost: float | None = None
        self.__storageCapacity: float | None = None
        self.__LCOS: float | None = None
        self.__inputElectricity: float | None = None
        self.__outputElectricity: float | None = None
        self.__roundtripEfficiency: float | None = None

    @abstractmethod
    def factory(self) -> AbstractElectricityStorageTechnology:
        raise NotImplementedError  # pragma: no cover

    def resetGhostProperties(self):

        self.__workingCycleDuration = None
        self.__wholeCycleDuration = None
        self.__standbyDuration = None
        self.__maximumFrequency = None
        self.__investmentCost = None
        self.__storageCapacity = None
        self.__LCOS = None
        self.__inputElectricity = None
        self.__outputElectricity = None
        self.__roundtripEfficiency = None

    @staticmethod
    def _assign(obj, *,
                dischargeDuration: float | None = None,  # nominal discharge duration [s]
                dischargingPower: float | None = None,  # nominal discharging power [W]
                chargeDuration: float | None = None,  # nominal charge duration [s]
                chargingPower: float | None = None,  # nominal charging power [W]
                roundtripEfficiency: float | None = None,  # (x > 0)
                powerIslandSpecificCost: float | None = None,  # [$/kW]
                storeSpecificCost: float | None = None,  # [$/kWh]
                selfDischargeRate: float | None = None,  # [%/h]
                secondarySource: str | None = None,  # secondary fuel used upon discharge (optional)
                secondaryConsumptionRatio: float | None = None,  # gas consumption ratio upon discharge [kWh_g / kWh_e]
                electricityPrice: float | None = None,  # [$/MWh]
                gasPrice: float | None = None,  # [$/MWh]
                hydrogenPrice: float | None = None,  # [$/MWh]
                frequency: float | None = None,  # number of cycles per year [#/year]
                currency: str | None = None,
                lifetime: int | None = None,
                discountRate: float | None = None,
                standby: float | None = None
                ):

        # Check validity of dischargeDuration and assign if correct
        if dischargeDuration is not None:
            if dischargeDuration >= 0:
                obj._dischargeDuration = dischargeDuration
            else:
                raise ValueError('dischargeDuration must be positive.')

        # Check validity of chargeDuration and assign if correct
        if chargeDuration is not None:
            if chargeDuration >= 0:
                obj._chargeDuration = chargeDuration
            else:
                raise ValueError('chargeDuration must be positive.')

        # Check validity of dischargingPower and assign if correct
        if dischargingPower is not None:
            if dischargingPower >= 0:
                obj._dischargingPower = dischargingPower
            else:
                raise ValueError('dischargingPower must be positive.')

        # Check validity of chargingPower and assign if correct
        if chargingPower is not None:
            if chargingPower >= 0:
                obj._chargingPower = chargingPower
            else:
                raise ValueError('chargingPower must be positive.')

        # Check validity of round-trip efficiency and assign if correct
        if roundtripEfficiency is not None:
            if 0 <= roundtripEfficiency:
                obj._roundtripEfficiency = roundtripEfficiency
            else:
                raise ValueError('Electricity-to-electricity roundtrip efficiency must be greater than 0.')

        # Check / enforce validity of energy input / output
        W_in = obj.nominalChargingPower_MW
        dt_in = obj.nominalChargeDuration_hours
        W_out = obj.nominalDischargingPower_MW
        dt_out = obj.nominalDischargeDuration_hours
        eta = obj.nominalRoundTripEfficiency
        parameters = [W_in, dt_in, W_out, dt_out, eta]
        if None not in parameters:
            if not np.isclose((W_out * dt_out) / (W_in * dt_in), eta):
                raise ValueError("Inconsistent charge/discharge and efficiency values.")
        elif parameters.count(None) == 1:
            if dt_in is None:
                obj._chargeDuration = W_out * dt_out / (eta * W_in) * 3600
            elif W_in is None:
                obj._chargingPower = W_out * dt_out / (eta * dt_in) / 1e6
            elif eta is None:
                obj._roundtripEfficiency = (W_out * dt_out) / (W_in * dt_in)
            elif dt_out is None:
                obj._dischargeDuration = eta * W_in * dt_in / W_out * 3600
            elif W_out is None:
                obj._dischargingPower = eta * W_in * dt_in / dt_out / 1e6

        # Check validity of powerIslandSpecificCost_per_kW and assign if correct
        if powerIslandSpecificCost is not None:
            if powerIslandSpecificCost >= 0:
                obj._powerIslandSpecificCost = powerIslandSpecificCost
            else:
                raise ValueError('powerIslandSpecificCost_per_kW must be positive.')

        # Check validity of storeSpecificCost_per_kWh and assign if correct
        if storeSpecificCost is not None:
            if storeSpecificCost >= 0:
                obj._storeSpecificCost = storeSpecificCost
            else:
                raise ValueError('storeSpecificCost_per_kWh must be positive.')

        # Check validity of electricityPrice and assign if correct
        if electricityPrice is not None:
            if electricityPrice >= 0:
                obj._electricityPrice = electricityPrice
            else:
                raise ValueError('electricityPrice must be positive.')

        # Check validity of gasPrice and assign if correct
        if gasPrice is not None:
            if gasPrice >= 0:
                obj._gasPrice = gasPrice
            else:
                raise ValueError('gasPrice must be positive.')

        # Check validity of hydrogenPrice and assign if correct
        if hydrogenPrice is not None:
            if hydrogenPrice >= 0:
                obj._hydrogenPrice = hydrogenPrice
            else:
                raise ValueError('hydrogenPrice must be positive.')

        # Check validity of secondaryConsumptionRatio and assign if correct
        if secondaryConsumptionRatio is not None:
            if secondaryConsumptionRatio >= 0:
                obj._secConsumptionRatio = secondaryConsumptionRatio
            else:
                raise ValueError('secondaryConsumptionRatio must be positive.')

        # Check validity of self-discharge rate and assign if correct
        if selfDischargeRate is not None:
            if 0 <= selfDischargeRate <= 1:
                obj._selfDischargeRate = selfDischargeRate
            else:
                raise ValueError('Self-discharge rate must lie between 0 and 1')

        # Check validity of the secondary source and assign if correct
        if secondarySource is not None:
            if secondarySource in ['electricity', 'gas', 'hydrogen']:
                obj._secSource = secondarySource
            else:
                raise ValueError('Secondary fuel must be either electricity, gas or hydrogen.')

        # Check validity of currency and assign if correct
        if currency is not None:
            if currency in ['USD', 'GBP', 'EUR']:
                obj._currency = currency
            else:
                raise ValueError('Currency must be either "USD", "GBP" or "EUR".')

        # Check validity of frequency and assign if correct
        if frequency is not None:
            if frequency >= 0:
                obj._frequency = frequency
            else:
                raise ValueError('Frequency must be greater than 1.')

        # Check validity of lifetime and assign if correct
        if lifetime is not None:
            if lifetime >= 1:
                obj._lifetime = lifetime
            else:
                raise ValueError('Lifetime must be an integer greater than 1.')

        # Check validity of discount rate and assign if correct
        if discountRate is not None:
            if 0 <= discountRate <= 1:
                obj._discountRate = discountRate
            else:
                raise ValueError('Discount rate must lie between 0 and 1')

        # Check validity of non-dimensional standby duration and assign if correct
        if standby is not None:
            if 0 <= standby <= 1:
                obj._standby = standby
            else:
                raise ValueError('standby rate must lie between 0 and 1')

        return obj

    def updateDiscountRate(self, discountRate: float):

        if 0 <= discountRate <= 1:
            self._discountRate = discountRate
        else:
            raise ValueError('Discount rate must lie between 0 and 1.')

    def updateEnergyPrices(self, *,
                           electricity: float | None = None,
                           gas: float | None = None,
                           hydrogen: float | None = None):

        if electricity is not None:
            if electricity >= 0:
                self._electricityPrice = electricity
            else:
                raise ValueError('Electricity price must be positive.')

        if gas is not None:
            if gas >= 0:
                self._gasPrice = gas
            else:
                raise ValueError('Gas price must be positive.')

        if hydrogen is not None:
            if hydrogen >= 0:
                self._hydrogenPrice = hydrogen
            else:
                raise ValueError('Hydrogen price must be positive.')

    """ System designation """
    """ ------------------ """

    @property
    def type(self):
        return self._type

    """ Battery technical characteristics (size) """
    """ ---------------------------------        """

    @property
    def nominalDischargeDuration_hours(self):

        if self._dischargeDuration is None:
            return None
        else:
            return self._dischargeDuration / 3600

    @property
    def nominalChargeDuration_hours(self):

        if self._chargeDuration is None:
            return None
        else:
            return self._chargeDuration / 3600

    @property
    def nominalDischargingPower_MW(self):

        if self._dischargingPower is None:
            return None
        else:
            return self._dischargingPower / 1e6

    @property
    def nominalChargingPower_MW(self):

        if self._chargingPower is None:
            return None
        else:
            return self._chargingPower / 1e6

    """ Technical performance """
    """ --------------------- """

    @property
    def nominalRoundTripEfficiency(self):
        return self._roundtripEfficiency

    @property
    def selfDischargeRate_percentPerHour(self):
        return self._selfDischargeRate

    @property
    def secondarySource(self) -> list:

        if self._secSource is None:
            return []
        else:
            return [self._secSource]

    """ Secondary fuel / energy vector """
    """ ------------------------------ """

    @property
    def secondarySourceConsumptionRatio(self) -> float | None:  # Q_sec / W_out [kWh_sec / kWh_e]
        return self._secConsumptionRatio

    @property
    def secondarySourceInput_MWh(self) -> float | None:  # Q_sec / W_out [kWh_sec / kWh_e]

        if not self.secondarySourceConsumptionRatio:
            return 0.
        else:
            r = self.secondarySourceConsumptionRatio
            W_out = self.outputElectricity_MWh
            if None not in [W_out, r]:
                return W_out * r
            else:
                return None

    """ Economic value """
    """ -------------- """

    @property
    def powerIslandSpecificCost_per_kW(self) -> float | None:
        return self._powerIslandSpecificCost

    @property
    def storeSpecificCost_per_kWh(self) -> float | None:
        return self._storeSpecificCost

    """ Economic conditions (scenario- & country-dependent parameters) """
    """ -------------------                                            """

    @property
    def electricityPrice(self) -> float | None:
        return self._electricityPrice

    @property
    def gasPrice(self) -> float | None:
        return self._gasPrice

    @property
    def hydrogenPrice(self) -> float | None:
        return self._hydrogenPrice

    @property
    def discountRate(self) -> float | None:
        return self._discountRate

    """ Utilisation / operational parameters """
    """ ------------------------------------ """

    @property
    def lifetime(self) -> int | None:
        return self._lifetime

    @property
    def frequency(self) -> float | None:
        if self._frequency is not None:
            return self.maximumFrequency if self._frequency > self.maximumFrequency else self._frequency
        else:
            return None

    """ Dependent properties """
    """ -------------------- """

    @property
    def wholeCycleDuration_hours(self) -> float | None:

        if self.__wholeCycleDuration is None:
            f = self.frequency
            if f is not None:
                self.__wholeCycleDuration = 8760 / f
        return self.__wholeCycleDuration

    @property
    def standbyDuration_hours(self) -> float | None:

        if self.__standbyDuration is None:
            dt = self.wholeCycleDuration_hours
            dt_w = self.workingCycleDuration_hours
            dt_norm_stb = self._standby
            if None not in [dt, dt_w, dt_norm_stb]:
                dt_idle = dt - dt_w
                self.__standbyDuration = dt_norm_stb * dt_idle
        return self.__standbyDuration

    @property
    def workingCycleDuration_hours(self) -> float | None:

        if self.__workingCycleDuration is None:

            dt_discharge = self.nominalDischargeDuration_hours  # [s]
            dt_charge = self.nominalChargeDuration_hours  # [h]

            if None not in [dt_discharge, dt_charge]:
                self.__workingCycleDuration = (dt_discharge + dt_charge)

        return self.__workingCycleDuration

    @property
    def storageCapacity_MWh(self) -> float | None:

        if self.__storageCapacity is None:

            # Gather inputs parameters
            dt = self._dischargeDuration  # [s]
            W = self._dischargingPower  # [W]

            if None not in [W, dt]:
                self.__storageCapacity = W * dt / 3600 / 1e6

        return self.__storageCapacity

    @property
    def investmentCost(self) -> float | None:

        if self.__investmentCost is None:

            # Gather inputs parameters
            cost_per_kW = self.powerIslandSpecificCost_per_kW  # [$/kW]
            cost_per_kWh = self.storeSpecificCost_per_kWh  # [$/kWh]
            MW = self.nominalDischargingPower_MW
            MWh = self.storageCapacity_MWh

            if None not in [MW, MWh, cost_per_kWh, cost_per_kW]:
                self.__investmentCost = MW * cost_per_kW * 1e3 + MWh * cost_per_kWh * 1e3

        return self.__investmentCost

    @property
    def maximumFrequency(self) -> int | None:

        if self.__maximumFrequency is None:

            # Gather inputs parameters
            cycleDuration = self.workingCycleDuration_hours

            if cycleDuration is not None:
                self.__maximumFrequency = int(8760 / cycleDuration)

        return self.__maximumFrequency

    @property
    def inputElectricity_MWh(self) -> float | None:

        if self.__inputElectricity is None:

            # Gather inputs parameters
            MW = self.nominalChargingPower_MW
            hours = self.nominalChargeDuration_hours

            if None not in [MW, hours]:
                self.__inputElectricity = MW * hours

        return self.__inputElectricity

    @property
    def outputElectricity_MWh(self) -> float | None:

        if self.__outputElectricity is None:

            # Gather inputs parameters
            W_in = self.inputElectricity_MWh
            dWdt = self.selfDischargeRate_percentPerHour / 100
            dt_stb = self.standbyDuration_hours
            eta = self.nominalRoundTripEfficiency

            if None not in [W_in, dWdt, dt_stb, eta]:
                W_st = W_in * (1 - dWdt) ** dt_stb
                self.__outputElectricity = eta * W_st if W_st > 0 else 0

        return self.__outputElectricity

    @property
    def roundtripEfficiency(self):

        if self.__roundtripEfficiency is None:

            W_in = self.inputElectricity_MWh
            W_out = self.outputElectricity_MWh

            if None not in [W_in, W_out]:
                self.__roundtripEfficiency = W_out / W_in

        return self.__roundtripEfficiency

    @property
    def levelisedCostOfStorage(self) -> float | list[float] | None:

        if self.__LCOS is None:

            # Gather inputs parameters
            investmentCost = self.investmentCost
            W_in_MWh = self.inputElectricity_MWh
            W_out_MWh = self.outputElectricity_MWh
            i = self.discountRate
            n = self.lifetime
            f = self.frequency
            C_el = self.electricityPrice  # $/MWh
            Q_sec_Mwh = self.secondarySourceInput_MWh
            C_sec = 0 if not self.secondarySource \
                else self.gasPrice if self.secondarySource[0] == 'gas' \
                else self.hydrogenPrice if self.secondarySource[0] == 'hydrogen' \
                else None

            if None not in [investmentCost, i, n, W_in_MWh, W_out_MWh, f, Q_sec_Mwh, C_sec]:

                n = np.arange(1, n)
                discount = (1 + i) ** n

                # Upfront costs
                C_inv = investmentCost

                # Discounted operational costs
                yearlyConsumption = W_in_MWh * C_el * f + Q_sec_Mwh * C_sec * f
                C_op = (yearlyConsumption / discount).sum()

                # Discounted electricity recovered
                yearlyDischarge = W_out_MWh * f
                W_kWh = (yearlyDischarge / discount).sum()

                self.__LCOS = (C_inv + C_op) / W_kWh  # [$/kWh]

        return self.__LCOS


""" SYSTEMS """


class ElectricityStorageTechnology(AbstractElectricityStorageTechnology):

    def __init__(self):
        super().__init__()

    def factory(self) -> ElectricityStorageTechnology:
        return ElectricityStorageTechnology()

    def withInputs(self, *,
                   dischargeDuration: float | None = None,  # nominal discharge duration [s]
                   dischargingPower: float | None = None,  # nominal discharging power [W]
                   chargeDuration: float | None = None,  # nominal charge duration [s]
                   chargingPower: float | None = None,  # nominal charging power [W]
                   roundtripEfficiency: float | None = None,  # (instantaneous) roundtrip efficiency (x > 0)
                   powerIslandSpecificCost: float | None = None,  # power-specific cost of the power island [$/kW]
                   storeSpecificCost: float | None = None,  # energy-specific cost of the store [$/kWh]
                   selfDischargeRate: float = 0,  # self-discharge rate [%/h]
                   secondarySource: str | None = None,  # secondary fuel used upon discharge (optional)
                   secondaryConsumptionRatio: float | None = 0,  # gas consumption ratio upon discharge [kWh_g / kWh_e]
                   currency: str = 'USD',
                   discountRate: float | None = None,
                   frequency: float | None = None,
                   lifetime: int | None = None,
                   standby: float | None = 1.) -> ElectricityStorageTechnology:

        obj = self.factory()

        # Assign input parameters
        obj._assign(
            obj,
            dischargeDuration=dischargeDuration,
            dischargingPower=dischargingPower,
            chargeDuration=chargeDuration,
            chargingPower=chargingPower,
            roundtripEfficiency=roundtripEfficiency,
            powerIslandSpecificCost=powerIslandSpecificCost,
            storeSpecificCost=storeSpecificCost,
            selfDischargeRate=selfDischargeRate,
            secondarySource=secondarySource,
            secondaryConsumptionRatio=secondaryConsumptionRatio,
            frequency=frequency,
            currency=currency,
            lifetime=lifetime,
            discountRate=discountRate,
            standby=standby)

        return obj


class ConventionalCAES(AbstractElectricityStorageTechnology):

    def __init__(self):

        super().__init__()

        self._type = 'D-CAES'
        self._model = 'PNNL'

        # PNNL performance metrics
        exergyEfficiency = 0.52  # Wout / (Win + Wg)
        carnotEfficiency = 0.49  # Wg / Qg
        roundtripEfficiency = 0.746  # Wout / Win

        # Power island cost data from PNNL (https://www.pnnl.gov/compressed-air-energy-storage-caes)
        duration = [1, 4, 10, 24, 100, 8000,
                    1, 4, 10, 24, 100, 8000]  # hours
        power = [100, 100, 100, 100, 100, 100,
                 1000, 1000, 1000, 1000, 1000, 1000]  # MW
        specificCost = [1050.28, 1050.28, 1048.93, 1048.41, 1048.13, 1048.13,
                        967.81, 967.81, 966.47, 965.94, 965.66, 965.66]  # USD / kW
        lowSpecificCost = [945.25, 945.25, 944.04, 943.57, 943.32, 943.32,
                           871.03, 871.03, 869.82, 869.35, 869.09, 869.09]  # USD / kW
        highSpecificCost = [1155.3, 1155.3, 1153.83, 1153.25, 1152.94, 1152.94,
                            1064.59, 1064.59, 1063.11, 1062.54, 1062.23, 1062.23]  # USD / kW

        # Scattered interpolant for power island SIC
        self._powerIslandSIC = LinearNDInterpolator(list(zip(duration, power)), specificCost)
        self._powerIslandLowSIC = LinearNDInterpolator(list(zip(duration, power)), lowSpecificCost)
        self._powerIslandHighSIC = LinearNDInterpolator(list(zip(duration, power)), highSpecificCost)

        # Salt cavern cost data from PNNL (https://www.pnnl.gov/compressed-air-energy-storage-caes)
        duration = [1, 4, 10, 24, 100, 8000,
                    1, 4, 10, 24, 100, 8000]  # hours
        power = [100, 100, 100, 100, 100, 100,
                 1000, 1000, 1000, 1000, 1000, 1000]  # MW
        specificCost = [11.2, 9.99, 7.64, 6.63, 5.89, 5.89,
                        6.5, 6.28, 5.89, 5.64, 5.32, 5.32]  # USD / kWh
        highSpecificCost = [16.59, 16.59, 16.54, 16.5, 16.44, 16.44,
                            16.48, 16.48, 16.44, 16.4, 16.33, 16.33]  # USD / kWh
        lowSpecificCost = [2.76, 2.76, 2.68, 2.6, 2.47, 2.47,
                           2.55, 2.55, 2.47, 2.39, 2.26, 2.26]  # USD / kWh

        # Scattered interpolant for store SIC
        self._saltCavernSIC = LinearNDInterpolator(list(zip(duration, power)), specificCost)
        self._saltCavernLowSIC = LinearNDInterpolator(list(zip(duration, power)), lowSpecificCost)
        self._saltCavernHighSIC = LinearNDInterpolator(list(zip(duration, power)), highSpecificCost)

        # Gas consumption ratio upon discharge [kWh_g / kWh_e]
        gasConsumptionRatio = 1 / carnotEfficiency * (1 / exergyEfficiency - 1 / roundtripEfficiency)  # = Qg / Wout

        # Assign input parameters
        self._assign(
            self,
            roundtripEfficiency=roundtripEfficiency,
            secondarySource='gas',
            secondaryConsumptionRatio=gasConsumptionRatio)

        # Additional ghost properties
        self.__powerIslandSpecificCost: list[float] | None = None
        self.__storeSpecificCost: list[float] | None = None
        self.__investmentCost: float | None = None

    def factory(self) -> ConventionalCAES:
        return ConventionalCAES()

    def resetGhostProperties(self):
        super().resetGhostProperties()

        # Additional ghost properties
        self.__powerIslandSpecificCost = None
        self.__storeSpecificCost = None
        self.__investmentCost = None

    def withInputs(self, *,
                   dischargeDuration: float | None = None,  # nominal discharge duration [s]
                   dischargingPower: float | None = None,  # nominal discharging power [W]
                   chargeDuration: float | None = None,  # nominal charge duration [s]
                   chargingPower: float | None = None,  # nominal charging power [W]
                   selfDischargeRate: float = 0,  # self-discharge rate [%/h]
                   currency: str = 'USD',
                   discountRate: float | None = None,
                   frequency: float | None = None,
                   lifetime: int | None = None,
                   standby: float | None = 1.) -> ConventionalCAES:

        obj = self.factory()

        # Assign input parameters
        obj._assign(
            obj,
            dischargeDuration=dischargeDuration,
            dischargingPower=dischargingPower,
            chargeDuration=chargeDuration,
            chargingPower=chargingPower,
            selfDischargeRate=selfDischargeRate,
            frequency=frequency,
            currency=currency,
            lifetime=lifetime,
            discountRate=discountRate,
            standby=standby)

        return obj

    def defineDesign(self, *,
                     dischargeDuration: float | None = None,  # nominal discharge duration [s]
                     dischargingPower: float | None = None,  # nominal discharging power [W]
                     chargeDuration: float | None = None,  # nominal charge duration [s]
                     chargingPower: float | None = None,  # nominal charging power [W]
                     selfDischargeRate: float = 0,  # self-discharge rate [%/h]
                     lifetime: int | None = None
                     ):

        self.resetGhostProperties()
        self._assign(obj=self,
                     dischargeDuration=dischargeDuration,
                     dischargingPower=dischargingPower,
                     chargeDuration=chargeDuration,
                     chargingPower=chargingPower,
                     selfDischargeRate=selfDischargeRate,
                     lifetime=lifetime)

    def defineOperatingConditions(self,
                                  frequency: float | None = None,  # number of cycles per year [#/year]
                                  standby: float | None = None
                                  ):

        self.resetGhostProperties()
        self._assign(obj=self,
                     frequency=frequency,
                     standby=standby)



    @property
    def model(self) -> str:
        return self._model

    """ Economic value """
    """ -------------- """

    @property
    def powerIslandSpecificCost_per_kW(self) -> list[float] | None:

        if self.__powerIslandSpecificCost is None:

            baseCEPCI = CEPCI[2023]
            hours = self.nominalDischargeDuration_hours
            MW = self.nominalDischargingPower_MW

            if None not in [hours, MW]:

                # Specific cost interpolation
                cost = self._powerIslandSIC(hours, MW)
                lowCost = self._powerIslandLowSIC(hours, MW)
                highCost = self._powerIslandHighSIC(hours, MW)

                # Inflation
                cost = cost * (CEPCI[CEPCI.index[-1]] / baseCEPCI)
                lowCost = lowCost * (CEPCI[CEPCI.index[-1]] / baseCEPCI)
                highCost = highCost * (CEPCI[CEPCI.index[-1]] / baseCEPCI)

                self.__powerIslandSpecificCost = [lowCost, cost, highCost]

        return self.__powerIslandSpecificCost

    @property
    def storeSpecificCost_per_kWh(self) -> list[float] | None:

        if self.__storeSpecificCost is None:

            baseCEPCI = CEPCI[2023]
            hours = self.nominalDischargeDuration_hours
            MW = self.nominalDischargingPower_MW

            if None not in [hours, MW]:

                # Specific cost interpolation
                cost = self._saltCavernSIC(hours, MW)
                lowCost = self._saltCavernLowSIC(hours, MW)
                highCost = self._saltCavernHighSIC(hours, MW)

                # Inflation
                cost = cost * (CEPCI[CEPCI.index[-1]] / baseCEPCI)
                lowCost = lowCost * (CEPCI[CEPCI.index[-1]] / baseCEPCI)
                highCost = highCost * (CEPCI[CEPCI.index[-1]] / baseCEPCI)

                self.__storeSpecificCost = [lowCost, cost, highCost]

        return self.__storeSpecificCost

    @property
    def investmentCost(self) -> list[float] | None:

        if self.__investmentCost is None and self.powerIslandSpecificCost_per_kW is not None:

            self.__investmentCost = []

            for n in np.arange(len(self.powerIslandSpecificCost_per_kW)):

                # Gather inputs parameters
                cost_per_kW = self.powerIslandSpecificCost_per_kW[n]  # [$/kW]
                cost_per_kWh = self.storeSpecificCost_per_kWh[n]  # [$/kWh]
                MW = self.nominalDischargingPower_MW
                MWh = self.storageCapacity_MWh

                if None not in [MW, MWh, cost_per_kWh, cost_per_kW]:

                    kWh = MWh * 1e3
                    kW = MW * 1e3

                    self.__investmentCost.append(kW * cost_per_kW + kWh * cost_per_kWh)

        return self.__investmentCost


class DiabaticCAES(AbstractElectricityStorageTechnology):

    def __init__(self):
        super().__init__()

        self._type = 'D-CAES'
        self._model = 'firstLaw'

    def factory(self) -> DiabaticCAES:
        return DiabaticCAES()

    def withDesign(self, *,
                   dischargeDuration: float | None = None,  # nominal discharge duration [s]
                   power: float | None = None,  # nominal discharging power [W]
                   selfDischargeRate: float = 0  # self-discharge rate [%/h]
                   ) -> DiabaticCAES:
        obj = self.factory()

        # Assign input parameters
        obj._assign(
            obj,
            dischargeDuration=dischargeDuration,
            dischargingPower=power,
            chargingPower=power,
            selfDischargeRate=selfDischargeRate,
            roundtripEfficiency=self._roundtripEfficiency,
            secondarySource=self._secSource,
            secondaryConsumptionRatio=self._secConsumptionRatio)

        return obj

    @property
    def model(self) -> str:
        return self._model
