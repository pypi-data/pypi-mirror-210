"""This module contains implementation for gradient blocks"""
__all__ = ["Gradient", "TrapezoidalGradient", "ArbitraryGradient"]

from typing import Tuple
from warnings import warn
import numpy as np
from pint import Quantity

from cmrseq.core.bausteine._base import SequenceBaseBlock
from cmrseq.core._system import SystemSpec


class Gradient(SequenceBaseBlock):
    """

    """
    #: Tuple containing defining points of gradient waveforms as np.array (wrapped as Quantity)
    #: with shape (time: (t, ), waveform: (3, t)). Between points, linear interpolation is assumed
    gradients: Tuple[Quantity, Quantity] = None

    def __add__(self, other) -> (Quantity, Quantity):
        """ Add to gradient definition and always returns a Tuple (time_points[n], waveforms[3, n])

        :param other:
        :return:
        """

        if isinstance(other, Gradient):
            tother, wfother = other.gradients
        elif isinstance(other, tuple):
            if len(other) != 2 or any(not isinstance(o, Quantity) for o in other):
                raise NotImplementedError
            tother, wfother = other
            if len(tother) == 0:
                return self.gradients
        else:
            raise NotImplementedError(f"Addition of {self.__class__} and {other.__class__} not "
                                      f"implemented")

        tself, wfself = self.gradients
        tother, wfother, tself, wfself = [np.around(_, decimals=10) for _ in
                                          [tother.m_as("ms"), wfother.m_as("mT/m"),
                                           tself.m_as("ms"), wfself.m_as("mT/m")]]
        if tother[-1] == tself[0] and np.allclose(wfother[:, -1], wfself[:, 0]):
            tother = tother[:-1]
            wfother = wfother[:, :-1]
        if tself[-1] == tother[0] and np.allclose(wfself[:, -1], wfother[:, 0]):
            tself = tself[:-1]
            wfself = wfself[:, :-1]
        t_combined = np.unique(np.sort([*tself, *tother]))
        wfself_interp = np.stack([np.interp(t_combined, tself, wf, left=0, right=0)
                                  for wf in wfself])
        wfother_interp = np.stack([np.interp(t_combined, tother, wf, left=0, right=0)
                                   for wf in wfother])
        wfself_interp[:, t_combined < tself[0]] = 0
        wfself_interp[:, t_combined > tself[-1]] = 0
        wfother_interp[:, t_combined < tother[0]] = 0
        wfother_interp[:, t_combined > tother[-1]] = 0
        return Quantity(t_combined, "ms"), Quantity(wfother_interp + wfself_interp, "mT/m")

    def __radd__(self, other):
        return self.__add__(other)

    def split(self, t: Quantity) -> (Quantity, Quantity):
        """ Splits the gradient waveform at given time and returns to new definining tuples
        that both include the split point.
        This output is meant to yield the original waveform when calling the __add__ functions on
        the result

        :param t:
        :return:
        """
        split_is_on_def = np.isclose(t.to("ms"), self.gradients[0].to("ms"))
        tself, wfself = self.gradients

        if np.any(split_is_on_def):
            split_index, = np.where(split_is_on_def)
            split_index = split_index[0]
            return (tself[:split_index+1], wfself[:, :split_index+1]), \
                   (tself[split_index:], wfself[:, split_index:])
        tself, wfself, t = tself.to("ms"), wfself.to("mT/m"), t.to("ms")
        insertion_index = np.searchsorted(tself, t)
        insertion_val = np.stack([np.interp(t, tself, wfself[i]) for i in range(3)])
        wfself = Quantity(np.insert(wfself, insertion_index, insertion_val, axis=1), "mT/m")
        tself = Quantity(np.insert(tself, insertion_index, t), "ms")
        split_index = insertion_index
        return (tself[:split_index+1], wfself[:, :split_index+1]), \
               (tself[split_index:], wfself[:, split_index:])

    @property
    def tmin(self) -> Quantity:
        return self.gradients[0][0]

    @property
    def tmax(self) -> Quantity:
        return self.gradients[0][-1]

    def scale_gradients(self, factor: float) -> None:
        """ Scales gradients by given factor if gradients are defined.

        :param factor: factor to globally scale the amplitude of gradient defintion.
        """
        t, grads = self.gradients
        self.gradients = (t, factor * grads)

    def rotate_gradients(self, rotation_matrix: np.ndarray) -> None:
        """ Rotates gradients to according to the gradient axes transformation:

        [[1 0 0][0 1 0][0 0 0]].T -> rotation matrix

        :raises: ValueError - if rotation_matrix is not valid : must be an orthogonal matrix

        :param rotation_matrix: (3, 3) rotation matrix containing the new column basis vectors
                                (meaning in [:, i], i indexes the new orientation of MPS).
                                Vectors are normalized along axis=0 to ensure same magnitude
        """
        valid_rotation = np.all(np.isclose((np.matmul(rotation_matrix, rotation_matrix.T)),
                                           np.identity(3), rtol=1e-10))
        if not valid_rotation:
            raise ValueError(f"Rotation matrix is not valid\n {np.matmul(rotation_matrix, rotation_matrix.T)} \n"
                             f"should be identity")

        t, wf = self.gradients
        vector_norms = np.linalg.norm(rotation_matrix, axis=0, keepdims=True)
        rotation_matrix = rotation_matrix / vector_norms
        wf_rot = np.einsum("it, ij -> jt", wf.m_as("mT/m"), rotation_matrix)
        self.gradients = (t, Quantity(wf_rot, "mT/m"))

    def _clean(self):
        """ If gradient definition contains duplicate consecutive points, the second one is
        removed"""
        deltat = np.diff(np.around(self.gradients[0].to("ms").m, decimals=6), axis=0)
        deltag = np.diff(np.around(self.gradients[1].to("mT/m").m, decimals=6), axis=1)
        duplicate_idx = np.where(np.logical_and(deltat == 0., np.all(deltag == 0., axis=0)))
        t, g = self.gradients
        cleaned_t = Quantity(np.delete(t.m_as("ms"), duplicate_idx), "ms")
        cleaned_g = Quantity(np.delete(g.m_as("mT/m"), duplicate_idx, axis=1), "mT/m")
        self.gradients = (cleaned_t, cleaned_g)

    def validate(self, system_specs: SystemSpec) -> None:
        """ Validates if the contained gradient_definition is valid for the given system-
        specifications.
        """
        max_grad_in_specs = np.all(np.abs(self.gradients[1].m_as("mT/m"))
                                   <= system_specs.max_grad.m_as("mT/m"))
        grad_slew = (np.diff(self.gradients[1].m_as("mT/m"), axis=1) /
                     np.diff(self.gradients[0].m_as("ms"), axis=0)[np.newaxis])
        grad_slew_in_specs = np.all(np.around(grad_slew, decimals=6)
                                    <= system_specs.max_slew.m_as("mT/m/ms"))
        tgridded = self.gradients[0].m_as("ms") / system_specs.grad_raster_time.m_as("ms")
        grad_on_grid = np.allclose(tgridded, np.around(tgridded), rtol=1e-6)
        if not all([max_grad_in_specs, grad_slew_in_specs, grad_on_grid]):
            raise ValueError(f"Gradient definition of {self.name} invalid:\n"
                             f"\t- max grad: {max_grad_in_specs}\n"
                             f"\t- max slew: {grad_slew_in_specs}\n"
                             f"\t- definition on grid: {grad_on_grid}")

    def snap_to_raster(self, system_specs: SystemSpec):
        warn("When calling snap_to_raster the waveform points are simply rounded to their nearest"
             f"neighbour if the difference is below the relative tolerance. Therefore this in"
             f" not guaranteed to be precise anymore")
        time_ndt = np.around(self.gradients[0].m_as("ms") /
                             system_specs.grad_raster_time.m_as("ms"), decimals=0)
        time_ndt = time_ndt * system_specs.grad_raster_time.to("ms")
        self.gradients = (time_ndt.to("ms"), self.gradients[1].to("mT/m"))

    def shift(self, time_shift: Quantity) -> None:
        """Adds the time-shift to all gradient definition points"""
        self.gradients = (self.gradients[0] + time_shift.to("ms"), self.gradients[1])

    def flip(self, time_flip: Quantity = None):
        """Time reverses block by flipping about a given time point. If no
        time is specified, the center of this gradient block is choosen."""
        if time_flip is None:
            time_flip = self.tmin + (self.tmax - self.tmin) / 2
        self.gradients = (np.flip(time_flip.to("ms") - self.gradients[0], axis=0),
                          np.flip(self.gradients[1], axis=1))


class TrapezoidalGradient(Gradient):
    """ Module implementing a trapezoidal gradient pulse, from specified parameters"""

    # pylint: disable=R0913
    def __init__(self,
                 system_specs: SystemSpec,
                 orientation: np.ndarray,
                 amplitude: Quantity,
                 flat_duration: Quantity,
                 rise_time: Quantity,
                 fall_time: Quantity = None,
                 delay: Quantity = Quantity(0., "ms"),
                 name: str = "trapezoidal",
                 snap_to_raster: bool = False):
        r""" Defines a trapezoidal gradient pulse:

        **Diagram**:

        .. code-block:: python

            .                     |-flat_dur-|                                      .
            .                     ____________                                      .
            .          |-delay-| /            \           |      amplitude          .
            .          _________/              \______    |                         .
            .                  |--|         |--|                                    .
            .                rise_time    fall_time                                 .
            .          |--------duration-------|                                    .

        :param system_specs: System-Limit context (SystemSpec instance)
        :param orientation: np.array of shape (3, ). Vector defining the gradient orientation
                            in (gx, gy, gz) channels. Is normalized internally
        :param amplitude: Quantity[Tesla/Length] Desired amplitude of specified gradient pulse
        :param flat_duration: Quantity[Time] Duration of gradient-plateau
        :param rise_time: Quantity[Time] Duration of rising slope.
        :param fall_time: Quantity[Time] Duration falling slope. If not specified symmetric
                                rise/fall time is assumed.
        :param delay: Quantity[Time] Leading time without gradients
        """
        norm = np.linalg.norm(orientation)
        if norm > 0:
            orientation /= norm

        if fall_time is None:
            fall_time = rise_time

        time_points = np.around(np.stack([
            0, rise_time.m_as("ms"),
            rise_time.m_as("ms") + flat_duration.m_as("ms"),
            fall_time.m_as("ms") + rise_time.m_as("ms") + flat_duration.m_as("ms")]
        ), decimals=6)
        time_points = Quantity(time_points, "ms") + delay
        grads_amp = np.stack([Quantity(0, "mT/m"), amplitude, amplitude, 0.])
        grads = grads_amp[np.newaxis] * orientation[:, np.newaxis]
        self.gradients = (time_points, grads)
        super().__init__(system_specs=system_specs, name=name, snap_to_raster=snap_to_raster)

    @property
    def rise_time(self) -> Quantity:
        """ Duration of the first trapezoidal gradient slope """
        return self.gradients[0][1] - self.gradients[0][0]

    @property
    def fall_time(self) -> Quantity:
        """ Duration of the second trapezoidal gradient slope """
        return self.gradients[0][-1] - self.gradients[0][-2]

    @property
    def flat_duration(self) -> Quantity:
        """ Duration of the trapezoidal gradient plateau """
        return self.gradients[0][-2] - self.gradients[0][1]

    @property
    def amplitude(self) -> Quantity:
        """ Amplitude of the trapezoidal gradient plateau in mT/m"""
        warn("Deprecation Warning: Please use the new property 'magnitude', as amplitude will"
             "be used as signed amplitude per channel in the next release")
        return Quantity(np.linalg.norm(self.gradients[1][:, 1].m_as("mT/m")), "mT/m")

    @property
    def magnitude(self) -> Quantity:
        """ Magnitude (norm over spatial dimensions) of the trapezoidal
        gradient plateau in mT/m"""
        return Quantity(np.linalg.norm(self.gradients[1][:, 1].m_as("mT/m")), "mT/m")

    @property
    def signed_amplitude(self) -> Quantity:
        """ Signed amplitude the amplitude per gradient channel """
        return self.gradients[1][:, 1].to("mT/m")

    @property
    def area(self) -> Quantity:
        """ Area of the trapezoidal gradient:
         ((rise_time + fall_time + flat_duration) * amplitude)"""
        area = (self.rise_time / 2 + self.fall_time / 2 + self.flat_duration) * \
               self.gradients[1][:, 1]
        return np.abs(area)

    @classmethod
    def from_area(cls, system_specs: SystemSpec, orientation: np.ndarray, area: Quantity,
                  delay: Quantity = Quantity(0., "ms"),
                  name: str = "trapezoidal") -> 'TrapezoidalGradient':
        """Constructs the shortest Trapezoidal or triangular gradient pulse with specified area
         given the system limits:

         :raises AssertionError: If area < 0

         :param system_specs: System-Limit context (SystemSpec instance)
         :param area: Quantity[Tesla/Length*Time] Desired first moment of the Gradient Pulse
         :param orientation: np.array of shape (3, ). Vector defining the gradient orientation
                             in (gx, gy, gz) channels. Is normalized internally
         :param delay: Quantity[Time] Leading time without gradients, defaults to 0. ms
         :param name:
         :return: TrapezoidalGradient object
         """
        assert area.m >= 0
        amplitude, rise_time, flat_time = system_specs.get_shortest_gradient(area.to("mT/m*ms"))
        return TrapezoidalGradient(system_specs=system_specs, orientation=orientation,
                                   amplitude=amplitude.to("mT/m"),
                                   flat_duration=flat_time.to("ms"), rise_time=rise_time.to("ms"),
                                   delay=delay, name=name)

    @classmethod
    # pylint: disable=W1401
    def from_dur_area(cls, system_specs: SystemSpec, orientation: np.ndarray, duration: Quantity,
                      area: Quantity, delay: Quantity = Quantity(0., "ms"),
                      name: str = "trapezoidal") -> 'TrapezoidalGradient':
        """ Constructs the Trapezoidal or triangular gradient pulse with specified area and duration
        (flat + 2 ramp), given the system limits. Ramp time is calculated under the assumption of
        using maximal slew rate.
        Is equivalent to solving:

        .. math::
            a=amplitude, A=area, \delta=ramp, D=duration, s_m=max slew \n
            Triangular: \n
            A = a (D-\delta) \ \ and \ \ \delta * s_m= a \n
            \\rightarrow \delta = (D/2)-\sqrt{(D/2)^2 - A/s_m}

        :raises ValueError: - Duration is not on gradient raster time
                            - If area is not feasible with given duration and system limits \n
        :raises AssertionError: If area < 0
        :return: TrapezoidalGradient object
        """
        assert area.m >= 0
        amplitude, rise_time, flat_time = system_specs.get_shortest_gradient(area.to("mT/m*ms"))
        if duration < rise_time * 2 + flat_time:
            raise ValueError("Duration is too short. Area not feasible with given system limits")

        duration_raster = system_specs.time_to_raster(duration)
        if not np.isclose(duration.m_as("ms") - duration_raster.m_as("ms"), 0., rtol=1e-6):
            raise ValueError(f"Specified duration not on raster: {duration.m_as('ms'):1.6f}/"
                             f"{system_specs.grad_raster_time.m_as('ms'):1.6f} is not an integer")

        p_half = duration_raster / 2.
        q = area / (system_specs.max_grad / system_specs.minmax_risetime)  # pylint: disable=C0103
        radicant = (p_half ** 2 - q).to("ms**2")
        if np.isclose(radicant.m, 0., atol=1e-5):
            radicant = Quantity(0, "ms**2")
        rise_time = np.abs(p_half - np.sqrt(radicant))
        rise_time = system_specs.time_to_raster(rise_time, raster="grad")
        flat_duration = duration - 2 * rise_time
        amplitude = area / (duration - rise_time)
        return TrapezoidalGradient(system_specs=system_specs, orientation=orientation,
                                   amplitude=amplitude.to("mT/m"),
                                   flat_duration=flat_duration.to("ms"),
                                   rise_time=rise_time.to("ms"), delay=delay, name=name)

    @classmethod
    # pylint: disable=W1401
    def from_fdur_area(cls, system_specs: SystemSpec, orientation: np.ndarray,
                       flat_duration: Quantity, area: Quantity,
                       delay: Quantity = Quantity(0., "ms"), name: str = "trapezoidal"):
        """ Constructs the Trapezoidal or triangular (fdur=0) gradient pulse with specified area
        and flat duration, given the system limits. Ramp time is calculated under the assumption of
        using maximal slew rate. Is equivalent to solving:

        .. math::
            a=amplitude, A=area, \delta=ramp, \Delta=flatduration, s_m=max slew \n
            Triangular: \n
            A = a (\Delta + \delta) \ \ and \ \ \delta * s_m = a \n
            \\rightarrow \delta = -(\Delta/2) + \sqrt{(\Delta/2)^2 - A/s_m}

        :raises ValueError: - Flat duration is not on gradient raster time
        :raises ValueError: - If area is not feasible with given duration and system limits
        :raises AssertionError: If area < 0

        :return: TrapezoidalGradient object """
        assert area.m >= 0
        amplitude, rise_time, flat_time = system_specs.get_shortest_gradient(area.to("mT/m*ms"))
        if flat_duration < flat_time:
            raise ValueError("Flat duration is too short. Area not feasible with given "
                             "system limits")

        duration_raster = system_specs.time_to_raster(flat_duration, raster="grad")
        if not np.isclose(flat_duration.m_as("ms") - duration_raster.m_as("ms"), 0., rtol=1e-6):
            raise ValueError(f"Specified duration not on raster: {flat_duration.m_as('ms'):1.6f}/"
                             f"{system_specs.grad_raster_time.m_as('ms'):1.6f} is not an integer")

        p_half = flat_duration / 2.
        q = - area / (system_specs.max_grad / system_specs.minmax_risetime)  # pylint: disable=C0103
        radicant = (p_half ** 2 - q).to("ms**2")
        if np.isclose(radicant.m, 0., atol=1e-5):
            radicant = Quantity(0, "ms**2")
        rise_time = - p_half + np.sqrt(radicant)
        rise_time = system_specs.time_to_raster(rise_time, raster="grad")
        amplitude = area / (flat_duration + rise_time)
        return TrapezoidalGradient(system_specs=system_specs, orientation=orientation,
                                   amplitude=amplitude.to("mT/m"),
                                   flat_duration=flat_duration.to("ms"),
                                   rise_time=rise_time.to("ms"), delay=delay, name=name)

    @classmethod
    def from_dur_amp(cls, system_specs: SystemSpec, orientation: np.ndarray, duration: Quantity,
                     amplitude: Quantity, delay: Quantity = Quantity(0., "ms"),
                     name: str = "trapezoidal"):
        """ Constructs the Trapezoidal or triangular (fdur=0) gradient pulse with specified duration
                and amplitude, given the system limits. Ramp time is calculated under the
                assumption of using maximal slew rate.

        :raises ValueError: If duration is not on grid & If amplitude is not reachable within
                            specified duration / 2 with given system limits
        """
        duration_raster = system_specs.time_to_raster(duration)
        if not np.isclose(duration.m_as("ms") - duration_raster.m_as("ms"), 0., rtol=1e-6):
            raise ValueError(f"Specified duration not on raster: {duration.m_as('ms'):1.6f}/"
                             f"{system_specs.grad_raster_time.m_as('ms'):1.6f} is not an integer")

        if duration / 2 * system_specs.max_slew < amplitude:
            raise ValueError("Specified amplitude not reachable with given slewrate and duration")

        rise_time = system_specs.get_shortest_rise_time(amplitude)
        flat_duration = duration - 2 * rise_time
        return TrapezoidalGradient(system_specs=system_specs, orientation=orientation,
                                   amplitude=amplitude.to("mT/m"),
                                   flat_duration=flat_duration.to("ms"),
                                   rise_time=rise_time.to("ms"), delay=delay, name=name)

    @classmethod
    def from_fdur_amp(cls, system_specs: SystemSpec, orientation: np.ndarray,
                      flat_duration: Quantity, amplitude: Quantity,
                      delay: Quantity = Quantity(0., "ms"), name: str = "trapezoidal"):
        """ Constructs the Trapezoidal or triangular (fdur=0) gradient pulse with specified flat
        duration and amplitude, given the system limits. Ramp time is calculated under the
        assumption of using maximal slew rate.

        :raises ValueError: If flat_duration is not on grid
        """
        flat_duration_raster = system_specs.time_to_raster(flat_duration)
        if not np.isclose(flat_duration.m_as("ms") - flat_duration_raster.m_as("ms"),
                          0., rtol=1e-6):
            raise ValueError(f"Specified duration not on raster: {flat_duration.m_as('ms'):1.6f}/"
                             f"{system_specs.grad_raster_time.m_as('ms'):1.6f} is not an integer")

        rise_time = system_specs.get_shortest_rise_time(amplitude)
        return TrapezoidalGradient(system_specs=system_specs, orientation=orientation,
                                   amplitude=amplitude.to("mT/m"),
                                   flat_duration=flat_duration.to("ms"),
                                   rise_time=rise_time.to("ms"), delay=delay, name=name)

    @classmethod
    def from_fdur_farea(cls, system_specs: SystemSpec, orientation: np.ndarray,
                        flat_duration: Quantity, flat_area: Quantity,
                        delay: Quantity = Quantity(0., "ms"), name: str = "trapezoidal"):
        """ Constructs the Trapezoidal or triangular (fdur=0) gradient pulse with specified flat
        duration and flat_area, given the system limits. Ramp time is calculated under the
        assumption of using maximal slew rate.

        :raises ValueError: If flat_duration is not on grid
        """
        assert flat_area.m >= 0
        flat_duration_raster = system_specs.time_to_raster(flat_duration)
        if not np.isclose(flat_duration.m_as("ms") - flat_duration_raster.m_as("ms"),
                          0., rtol=1e-6):
            raise ValueError(f"Specified duration not on raster: {flat_duration.m_as('ms'):1.6f}/"
                             f"{system_specs.grad_raster_time.m_as('ms'):1.6f} is not an integer")

        amplitude = flat_area / flat_duration
        rise_time = system_specs.get_shortest_rise_time(amplitude)
        return TrapezoidalGradient(system_specs=system_specs, orientation=orientation,
                                   amplitude=amplitude.to("mT/m"),
                                   flat_duration=flat_duration.to("ms"),
                                   rise_time=rise_time.to("ms"), delay=delay, name=name)


class ArbitraryGradient(Gradient):
    """ Wraps a definition of an arbitrary waveform defined as numpy arrays."""

    def __init__(self, system_specs: SystemSpec,
                 time_points: Quantity,
                 waveform: Quantity,
                 delay: Quantity = Quantity(0, "ms"),
                 name: str = "name",
                 snap_to_raster: bool = False):
        """ Wraps a definition of waveform in numpy arrays.

        :param system_specs:
        :param time_points: Quantity[Time] - array of shape (#steps, ) containing the defining
                                time-points of the gradient waveform
        :param waveform: Quantity[Tesla/Length] - array of shape (3, #steps) containing the
                                gradient amplitudes corresponding to time_points
        """
        self.gradients = (time_points + delay, waveform)
        super().__init__(system_specs=system_specs, name=name, snap_to_raster=snap_to_raster)
