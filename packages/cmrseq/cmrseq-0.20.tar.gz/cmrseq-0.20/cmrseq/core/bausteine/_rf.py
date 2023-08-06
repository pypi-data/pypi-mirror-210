""" This module contains in the implementation of radio-frequency pulse building blocks"""
__all__ = ["RFPulse", "SincRFPulse","HardRFPulse", "ArbitraryRFPulse"]

from typing import Tuple
from warnings import warn

from pint import Quantity
import numpy as np

from cmrseq.core.bausteine._base import SequenceBaseBlock
from cmrseq.core._system import SystemSpec


class RFPulse(SequenceBaseBlock):
    """ RF-specific extension to the SequenceBaseBlock, serves as base class for all
    RF implementations"""
    #: Tuple containing defining points of RF-waveforms as np.array (wrapped as Quantity)
    #: with shape (time: (t, ), waveform: (3, t)). Between points, linear interpolation is assumed
    _rf: Tuple[Quantity, Quantity] = None

    #: Tuple containing rf events (time, flip_angle)
    rf_events: Tuple[Quantity, Quantity] = None

    #: RF pulse bandwidth in kilo Hertz. Used to calculate gradient strength
    bandwidth: Quantity

    #: RF phase offset in radians. This is used phase shift the complex rf amplitude in self.rf
    phase_offset: Quantity

    #: RF frequency offset in Hertz. This is used to modulate the complex rf amplitude in self.rf
    frequency_offset: Quantity

    def __init__(self, system_specs: SystemSpec, name: str, frequency_offset: Quantity,
                 phase_offset: Quantity, bandwidth: Quantity, snap_to_raster: bool):
        self.phase_offset = phase_offset.to("rad")
        self.frequency_offset = frequency_offset.to("Hz")
        self.bandwidth = bandwidth.to("kHz")
        super().__init__(system_specs, name, snap_to_raster)

    @property
    def tmin(self):
        return self._rf[0][0]

    def validate(self, system_specs: SystemSpec):
        """ Validates if the contained rf-definition is valid for the given system-
                specifications"""
        t, wf = self._rf
        float_steps = t.m_as("ms") / system_specs.rf_raster_time.m_as("ms")
        n_steps = np.around(float_steps)
        ongrid = np.allclose(n_steps, float_steps, rtol=1e-6)
        if not all([ongrid]):
            raise ValueError(f"RF definition invalid:\n"
                             f"\t - definition on grid: {ongrid}\n")

        if np.max(np.abs(wf)) > system_specs.rf_peak_power:
            raise ValueError(f"RF definition invalid:\n"
                             f"\t - peak power exceeds system limits: {np.max(np.abs(wf))}\n")

    @property
    def rf(self):
        """ Returns the complex RF-amplitude shifted/modulated by the phase/frequency offsets """
        t, amplitude = self._rf
        t_zero_ref = t - t[0]
        if amplitude.m_as("uT").dtype in [np.complex64, np.complex128]:
            complex_amplitude = np.array(amplitude.m_as("uT"))
        else:
            complex_amplitude = np.array((amplitude.m_as("uT") + 1j * np.zeros_like(amplitude.m_as("uT"))))
        phase_per_time = (self.phase_offset.m_as("rad") +
                          2 * np.pi * self.frequency_offset.m_as("kHz") * t_zero_ref.m_as("ms"))
        complex_amplitude = complex_amplitude * np.exp(1j * phase_per_time)
        return t, Quantity(complex_amplitude, "uT")

    @rf.setter
    def rf(self, value: Tuple[Quantity, Quantity]):
        self._rf = value

    @property
    def normalized_waveform(self) -> (np.ndarray, Quantity, np.ndarray, Quantity):
        """
        :return: - Normalized amplitude between [-1, 1] [dimensionless] (flipped such that the
                    maximum normalized value is positive. Scaling with peak amplitude inverts the
                    shape again)
                 - Peak amplitude in uT
                 - Phase per timestep in rad
                 - Time raster definition points
        """
        t, amplitude = self._rf
        t_zero_ref = t - t[0]
        if amplitude.m_as("uT").dtype in [np.complex64, np.complex128]:
            phase = np.angle(amplitude.m_as("uT"))
            phase = phase - self.phase_offset.m_as("rad")
            phase -= (t_zero_ref * 2 * np.pi * self.frequency_offset).m_as("rad")
            amplitude = amplitude.m_as("uT") * np.exp(-1j * phase)
        else:
            phase = np.zeros(amplitude.shape, dtype=np.float64)
            amplitude = amplitude.m_as("uT")

        peak_amp_plus, peak_amp_minus = np.max(amplitude), np.min(amplitude)
        absolute_max_idx = np.argmax([np.abs(peak_amp_plus), np.abs(peak_amp_minus)])
        peak_amp = (peak_amp_plus, peak_amp_minus)[absolute_max_idx]
        normed_amp = np.divide(amplitude, peak_amp, out=np.zeros_like(amplitude),
                               where=(peak_amp != 0))
        return np.real(normed_amp), Quantity(peak_amp, "uT"), phase, t_zero_ref

    def shift(self, time_shift: Quantity) -> None:
        """Adds the time-shift to all rf definition points and the rf-center"""
        time_shift =  time_shift.to("ms")
        self._rf = (self._rf[0] + time_shift, self._rf[1])
        self.rf_events = (self.rf_events[0] + time_shift, self.rf_events[1])

    def flip(self, time_flip: Quantity = None):
        """Time reverses block by flipping about a given time point. If no
        time is specified, the rf center of this block is choosen."""
        if time_flip is None:
            time_flip = self.rf_events[0][0]
        self._rf = (np.flip(time_flip.to("ms") - self._rf[0], axis=0), np.flip(self._rf[1], axis=1))
        self.rf_events = (np.flip(time_flip.to("ms") - self.rf_events[0], axis=0),
                          np.flip(self.rf_events[1], axis=0))

    def snap_to_raster(self, system_specs: SystemSpec):
        warn("When calling snap_to_raster the waveform points are simply rounded to their nearest"
             f"neighbour if the difference is below the relative tolerance. Therefore this in"
             f" not guaranteed to be precise anymore")

        t_rf = system_specs.time_to_raster(self._rf[0], "rf")
        self._rf = (t_rf.to("ms"), self._rf[1])


class SincRFPulse(RFPulse):
    """Defines a Sinc-RF pulse on a time grid with step length defined by system_specs. The
    window function used to temporally limit the waveform is given as:

    .. math::

        window = (1 - \\beta) + \\beta cos(2 \\pi n /N)

    where :math:`\\beta` is the specified apodization argument. If set to 0.5 the used window is a
    Hann window resulting in 0 start and end. using 0.46 results in the use of a Hamming window.

    .. warning::

        The sinc-pulse definition does not enforce 0 valued start and end of the wave-form.

    :param flip_angle: Quantity[Angle] Desired Flip angle of the Sinc Pulse. For negative
                        Values the flip-angle is stored as positive absolute plus a phase offset
                        of 180°
    :param duration: Quantity[Time] Total duration of the pulse
    :param time_bandwidth_product: float - Used to calculated the pulse-bandwidth. For a
                Sinc-Pulse bw = time_bandwidth_product/duration corresponds to the
                half central-lobe-width
    :param center: float [0, 1] factor to compute the pulse center relative to duration
    :param delay:
    :param apodization: float from interval [0, 1] used to calculate cosine-apodization window
    :param frequency_offset: Frequency offset in Hz in rotating frame ()
    :param phase_offset: Phase offset in rad.
    :param name:
    """
    # pylint: disable=R0913, R0914
    def __init__(self,
                 system_specs: SystemSpec,
                 duration: Quantity,
                 flip_angle: Quantity = Quantity(np.pi, "rad"),
                 time_bandwidth_product: float = 3.,
                 center: float = 0.5,
                 delay: Quantity = Quantity(0., "ms"),
                 apodization: float = 0.5,
                 frequency_offset: Quantity = Quantity(0., "Hz"),
                 phase_offset: Quantity = Quantity(0., "rad"),
                 name: str = "sinc_rf"):
        """ Defines a Sinc-RF pulse on a time grid with step length defined by system_specs.

        :param flip_angle: Quantity[Angle] Desired Flip angle of the Sinc Pulse. For negative
                            Values the flip-angle is stored as positive absolute plus a phase offset
                            of 180°
        :param duration: Quantity[Time] Total duration of the pulse
        :param time_bandwidth_product: float - Used to calculated the pulse-bandwidth. For a
                    Sinc-Pulse bw = time_bandwidth_product/duration corresponds to the
                    half central-lobe-width
        :param center: float [0, 1] factor to compute the pulse center relative to duration
        :param delay:
        :param apodization: float from interval [0, 1] used to calculate cosine-apodization window
        :param frequency_offset: Frequency offset in Hz in rotating frame ()
        :param phase_offset: Phase offset in rad.
        :param name:
        """

        if flip_angle < Quantity(0, "rad"):
            phase_offset += Quantity(np.pi, "rad")
            flip_angle = -flip_angle

        time_points, unit_wf = self._get_unit_waveform(
                                            raster_time=system_specs.rf_raster_time, 
                                            time_bandwidth_product=time_bandwidth_product,
                                            duration=duration, apodization=apodization,
                                            center=center)

        # For Sinc-Pulse this t*bw/duration corresponds to half central lobe width
        bandwidth = Quantity(time_bandwidth_product / duration.to("ms"), "1/ms")

        unit_flip_angle = np.sum((unit_wf[1:] + unit_wf[:-1]) / 2) * system_specs.rf_raster_time.to("ms")\
                          * system_specs.gamma_rad.to("rad/mT/ms")

        amplitude = unit_wf * flip_angle.to("rad") / unit_flip_angle

        self._rf = (time_points + delay, amplitude)
        self.rf_events = (center * duration + delay, flip_angle)

        super().__init__(system_specs=system_specs, name=name, frequency_offset=frequency_offset,
                         phase_offset=phase_offset, bandwidth=bandwidth, snap_to_raster=False)
    
    @staticmethod
    def _get_unit_waveform(raster_time: Quantity, time_bandwidth_product: float,
                           duration: Quantity,
                           apodization: float, center: float) -> Quantity:
        """ Constructs the sinc-pulse waveform according to:

        .. math:: 

            wf = (1 - \Gamma + \Gamma cos(2\pi / \Delta * t)) * sinc(tbw/\Delta t)

        where

        .. math::
            \Gamma     :& apodization (typically 0.46) \\\\
            \Delta     :& Pulse duration \\\\
            tbw        :& Time-bandwidth-product \\\\
            t          :& time on raster where center defines 0.


        """   
        bandwidth = Quantity(time_bandwidth_product / duration.m_as("ms"), "1/ms")
        n_steps = np.around(duration.m_as("ms") / raster_time.m_as("ms"))
        time_points = Quantity(np.arange(0., n_steps+1, 1) * raster_time.m_as("ms"), "ms")
        time_rel_center = time_points.to("ms") - (center * duration.to("ms"))
        window = (1 - apodization) + apodization * np.cos(2 * np.pi * np.arange(-n_steps//2, n_steps//2+1, 1) / n_steps)
        unit_wf = np.sinc((bandwidth.to("1/ms") * time_rel_center).m_as("dimensionless")) #* window
        return time_points, unit_wf * window

    @classmethod
    def from_shortest(cls, system_specs: SystemSpec, flip_angle: Quantity,  
                      time_bandwidth_product: float = 3., center: float = 0.5,
                      delay: Quantity = Quantity(0., "ms"), 
                      apodization: float = 0.46, 
                      frequency_offset: Quantity = Quantity(0., "Hz"), 
                      phase_offset: Quantity = Quantity(0., "rad"),
                      name: str = "sinc_rf"): 
        """
        
        """
        durations = Quantity(np.linspace(0.1, 1.5, 2), "ms")
        fas = []
        for dur in durations:
            _, unit_wf = cls._get_unit_waveform(raster_time=system_specs.rf_raster_time,
                                                time_bandwidth_product=time_bandwidth_product,
                                                duration=dur, apodization=apodization,
                                                center=center)
            max_wf =  unit_wf.m_as("dimensionless") * system_specs.rf_peak_power.to("uT")
            fa = np.sum((max_wf[1:] + max_wf[:-1]) / 2 * system_specs.rf_raster_time.to("ms"))
            fa *= system_specs.gamma_rad.to("rad/mT/ms") 
            fas.append(fa.m_as("degree"))
        slope = Quantity(np.diff(durations.m_as("ms")) / np.diff(fas), "ms/degree")
        target_duration = system_specs.time_to_raster(np.abs(flip_angle) * slope, "rf")
        
        return cls(system_specs, duration=target_duration,
                   flip_angle=flip_angle, time_bandwidth_product=time_bandwidth_product,
                   center=center, delay=delay, apodization=apodization,
                   frequency_offset=frequency_offset, phase_offset=phase_offset, name=name)
    
    # @classmethod
    # def from_bandwidth(cls, system_specs: SystemSpec,
    #                    band_width: Quantity,
    #                    flip_angle: Quantity,  
    #                    time_bandwidth_product: float = 4, 
    #                    center: float = 0.5,
    #                    delay: Quantity = Quantity(0., "ms"), 
    #                    apodization: float = 0., 
    #                    frequency_offset: Quantity = Quantity(0., "Hz"), 
    #                    phase_offset: Quantity = Quantity(0., "rad"),
    #                    name: str = "sinc_rf"):
    #     """
        
    #     """
    #     duration = Quantity(time_bandwidth_product / band_width.to("1/ms"), "ms")
    #     return cls(system_specs, duration=duration, flip_angle=flip_angle,
    #                time_bandwidth_product=time_bandwidth_product,
    #                center=center, delay=delay, apodization=apodization,
    #                frequency_offset=frequency_offset, phase_offset=phase_offset, name=name)

class HardRFPulse(RFPulse):
    """Defines a constant (hard) RF pulse on a time grid with step length defined by system_specs. """
    # pylint: disable=R0913, R0914
    def __init__(self,
                 system_specs: SystemSpec,
                 flip_angle: Quantity = Quantity(np.pi, "rad"),
                 duration: Quantity = Quantity(1., "ms"),
                 delay: Quantity = Quantity(0., "ms"),
                 frequency_offset: Quantity = Quantity(0., "Hz"),
                 phase_offset: Quantity = Quantity(0., "rad"),
                 name: str = "hard_rf"):
        """ Defines a constant (hard) RF pulse on a time grid with step length defined by system_specs.

        :param flip_angle: Quantity[Angle] Desired Flip angle of the RF Pulse. For negative
                            Values the flip-angle is stored as positive absolute plus a phase offset
                            of 180°
        :param duration: Quantity[Time] Total duration of the pulse
        :param delay:
        :param frequency_offset: Frequency offset in Hz in rotating frame ()
        :param phase_offset: Phase offset in rad.
        :param name:
        """

        if flip_angle < Quantity(0, "rad"):
            phase_offset += Quantity(np.pi, "rad")
            flip_angle = -flip_angle

        raster_time = system_specs.rf_raster_time.to("ms")
        n_steps = np.around(duration.m_as("ms") / raster_time.m_as("ms"))
        time_points = Quantity(np.arange(0., n_steps+1, 1) * raster_time.m_as("ms"), "ms")

        amplitude = (flip_angle/system_specs.gamma_rad/raster_time/(n_steps+1)).to('mT')
        self._rf = (time_points + delay, amplitude*np.ones_like(time_points))
        self.rf_events = (duration/2 + delay, flip_angle)

        super().__init__(system_specs=system_specs, name=name, frequency_offset=frequency_offset,
                         phase_offset=phase_offset, bandwidth=0.5/duration, snap_to_raster=False)

class ArbitraryRFPulse(RFPulse):
    """ Wrapper for arbitrary rf shapes, to adhere to building block concept. 
    The gridding is assumed to be on raster time and **not** shifted by half
    a raster time. This shift (useful for simulations) can be incorporated when
    calling the gridding function of the sequence.

    waveform is assumed to start and end with values of 0 uT

    :param system_specs:
    :param name:
    :param time_points: Shape (#steps)
    :param waveform: Shape (#steps) in uT as complex array
    :param bandwidth:
    :param frequency_offset:
    :param phase_offset:
    :param snap_to_raster:
    """
    def __init__(self, system_specs: SystemSpec, name: str,
                 time_points: Quantity,
                 waveform: Quantity,
                 delay: Quantity = Quantity(0., "ms"),
                 bandwidth: Quantity = None,
                 frequency_offset: Quantity = Quantity(0., "Hz"),
                 phase_offset: Quantity = Quantity(0., "rad"),
                 snap_to_raster: bool = False):
        """ 
        :param system_specs:
        :param name:
        :param time_points: Shape (#steps)
        :param waveform: Shape (#steps) in uT as complex array
        :param bandwidth:
        :param frequency_offset:
        :param phase_offset:
        :param snap_to_raster:
        """
        self._rf = (time_points.to("ms") + delay, waveform.to("mT"))
        if bandwidth is None:
            # TODO: estimate bandwidth of arbitrary rf pulses
            bandwidth = Quantity(0, "kHz")
        #TODO estimate phase offset and freqoffset from complex wf

        center = (time_points.to("ms")[-1] - time_points.to("ms")[0]) / 2 + time_points.to("ms")[0]
        flip_angle = system_specs.gamma_rad * Quantity(np.trapz(waveform.real.m_as("mT"), time_points.m_as("ms")), "mT ms")
        self.rf_events = (center, flip_angle.to("rad"))

        super().__init__(system_specs, name, frequency_offset=frequency_offset,
                         phase_offset=phase_offset, bandwidth=bandwidth,
                         snap_to_raster=snap_to_raster)


