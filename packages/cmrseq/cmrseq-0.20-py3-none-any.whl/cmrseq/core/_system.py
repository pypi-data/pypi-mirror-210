""" This Module contains the implementation of the core functionality SystemSpec """

__all__ = ["SystemSpec"]

from typing import Tuple

from pint import Quantity
import numpy as np


# pylint: disable=R0902, R0913, C0103
class SystemSpec():
    """ Specifications of MR-System limits. """
    #: Quantity[mT/m]: Maximum gradient amplitude
    max_grad: Quantity
    #: Quantity[mT/m/ms]: Maximum gradient slew rate
    max_slew: Quantity
    #: Quantity[uT]: Peak power for B1 fields (in micro tesla)
    rf_peak_power: Quantity
    #: Quantity[ms]: Not in use yet...
    rf_dead_time: Quantity
    #: Quantity[ms]: Not in use yet...
    rf_ringdown_time: Quantity
    #: Quantity[ms]: Not in use yet...
    adc_dead_time: Quantity
    #: Quantity[ms]: delta t of radio-frequency grid, defaults to 10us
    rf_raster_time: Quantity
    #: Quantity[ms]: delta t of gradient grid, defaults to 10us
    grad_raster_time: Quantity
    #: Quantity[ms]: delta t of adc grid, defaults to 10us
    adc_raster_time: Quantity
    #: Quantity[MHz/T]: Gyromagnetic ratio for nucleus the system is working on
    gamma: Quantity
    #: Quantity[rad/s/T]: Gyromagnetic ratio for nucleus the system is working on in rad/s
    gamma_rad: Quantity
    #: Flag to enable gradient validation and cleaning. Note functions may not work correctly
    # if False

    def __init__(self,
                 gamma: Quantity = Quantity(42.576, "MHz/T"),
                 grad_raster_time: Quantity = Quantity(1e-2, "ms"),
                 max_grad: Quantity = Quantity(40, "mT/m"),
                 max_slew: Quantity = Quantity(120, "mT/m/ms"),
                 rf_peak_power: Quantity = Quantity(30, "uT"),
                 rf_raster_time: Quantity = Quantity(1e-2, "ms"),
                 rf_dead_time: Quantity = Quantity(0., "ms"),
                 rf_ringdown_time: Quantity = Quantity(1e-3, "ms"),
                 adc_raster_time: Quantity = Quantity(1e-2, "ms"),
                 adc_dead_time: Quantity = Quantity(0., "ms"),
                 b0: Quantity = Quantity(1.5, "T")):

        if max_grad.to_base_units().units == Quantity(1., "1/m/s").units:
            max_grad = (max_grad * gamma).to("mT/m")

        if max_slew.to_base_units().units == Quantity(1., "1/m/s**2").units:
            max_slew = (max_slew * gamma).to("mT/m/ms")

        self.rf_peak_power = rf_peak_power.to("uT")
        self.rf_dead_time = rf_dead_time.to("ms")
        self.rf_ringdown_time = rf_ringdown_time.to("ms")
        self.adc_dead_time = adc_dead_time.to("ms")
        self.rf_raster_time = rf_raster_time.to("ms")
        self.grad_raster_time = grad_raster_time.to("ms")
        self.adc_raster_time = adc_raster_time.to("ms")
        self.gamma = gamma.to("MHz/T")
        self.gamma_rad = gamma.to("rad/T/s") * 2 * np.pi

        self.max_grad = max_grad
        self.max_slew = max_slew
        self.minmax_risetime = self.time_to_raster(np.around((max_grad / max_slew).to("ms"),
                                                             decimals=6))
        self.b0 = b0.to("T")

    def get_shortest_rise_time(self, delta_amplitude: Quantity) -> Quantity:
        """ Calculates the shortest ramp duration for the specified amplitude difference.

        :param delta_amplitude: Quantity[mT/m]
        :return: delta t - Quantity[ms] which is guaranteed to be a multiple of grad_raster_time
        """
        delta_amplitude = np.abs(delta_amplitude)
        shortest_ramp_dur = np.around((delta_amplitude / self.max_slew).to("ms"), decimals=6)
        return self.time_to_raster(shortest_ramp_dur, raster="grad")

    def get_shortest_gradient(self, area: Quantity) -> Tuple[Quantity, Quantity, Quantity]:
        """ Calculates the shortest gradient of a given area, obeying system limits

        :param area: Quantity[mT/m*s]
        :return: Tuple(amplitude, rise time, flat time)
        """

        if not area.check("T/m*s"):
            raise ValueError("Unit of gradient area incorrect, must be mT/m*s or equivalent")

        fastest_ramp = self.get_shortest_rise_time(self.max_grad)

        if fastest_ramp*self.max_grad > area:
            # Triangular
            ramp_time = np.sqrt(area/self.max_slew)
            ramp_time = self.time_to_raster(ramp_time, raster="grad")
            amplitude = area / ramp_time
            flat_time = Quantity(0., 'ms')
        else:
            # Trapezoid
            flat_time = area / self.max_grad - fastest_ramp
            flat_time = self.time_to_raster(flat_time, raster="grad")
            amplitude = area / (fastest_ramp + flat_time)
            ramp_time = fastest_ramp

        return amplitude, ramp_time, flat_time

    def time_to_raster(self, time: Quantity, raster: str = "grad") -> Quantity:
        """ Calculates the time projected onto the either gradient or rf raster.

        :param time: Quantity[s]
        :param raster: from [grad, rd]
        :return: Quantity[ms]
        """
        if raster.lower() == "grad":
            raster = self.grad_raster_time.to("ms")
        elif raster.lower() == "rf":
            raster = self.rf_raster_time.to("ms")
        elif raster.lower() == "adc":
            raster = self.adc_raster_time.to("ms")
        else:
            raise ValueError(f"Invalid raster choice: {raster} not in [grad, rf, adc]")
        time = np.around(time.m_as("ms"), decimals=8)
        time_ndt = np.ceil(np.around(time / raster.m_as("ms"),decimals=8))
        time_ndt = time_ndt * raster.to("ms")
        return time_ndt.to("ms")

    def __str__(self):
        return_string = "System limits:"
        return_string += "\n\tmax_grad: " + str(self.max_grad)
        return_string += "\n\tmax_slew: " + str(self.max_slew)
        return_string += "\n\trf_dead_time: " + str(self.rf_dead_time)
        return_string += "\n\trf_ring_time: " + str(self.rf_ringdown_time)
        return_string += "\n\tadc_dead_time: " + str(self.adc_dead_time)
        return_string += "\n\trf_raster_time: " + str(self.rf_raster_time)
        return_string += "\n\tgrad_raster_time: " + str(self.grad_raster_time)
        return_string += "\n\tadc_raster_time: " + str(self.adc_raster_time)
        return_string += "\n\tminmax_risetime:" + str(self.minmax_risetime)
        return_string += "\n\tgamma: " + str(self.gamma)
        return return_string
