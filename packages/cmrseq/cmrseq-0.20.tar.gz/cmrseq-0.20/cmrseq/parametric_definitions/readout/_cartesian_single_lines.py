""" This modules contains compositions of building blocks commonly used for in defining actual
signal acqusition and spatial encoding
"""
__all__ = ["multi_line_cartesian", "gre_cartesian_line", "balanced_gre_cartesian_line",
           "se_cartesian_line"]

from copy import deepcopy
import typing

from pint import Quantity
import numpy as np

import cmrseq


# pylint: disable=W1401, R0914
def multi_line_cartesian(system_specs: cmrseq.SystemSpec,
                         fnc: callable,
                         matrix_size: np.ndarray,
                         inplane_resolution: Quantity,
                         dummy_shots: int = None, **kwargs):
    """ Creates a list of sequences, one for each k-space_line for a given single-line-definiton
    e.g. se_cartesian_line, gre_cartesian_line

    **Example:**
    .. code-block: python

        ro_blocks = cmrseq.seqdefs.readout.multi_line_cartesian(
                                    system_specs=system_specs,
                                    fnc=cmrseq.seqdefs.readout.gre_cartesian_line,
                                    matrix_size=matrix_size,
                                    inplane_resolution=inplane_resolution,
                                    adc_duration=adc_duration,
                                    prephaser_duration=ss_refocus.duration,
                                    dummy_shots=dummy_shots)

    :param system_specs: SystemSpecification
    :param fnc: callable
    :param matrix_size: array of shape (2, )
    :param inplane_resolution: Quantity[Length] of shape (2, )
    :param dummy_shots: number of shots without adc-events
    :param kwargs: is forwared to call fnc. may not contain
                        num_samples, k_readout, k_phase, prephaser_duration
    :return:
    """
    kro_max = 1 / inplane_resolution[0]
    fov_pe = matrix_size[1] * inplane_resolution[1]
    delta_kpe = 1 / fov_pe
    if matrix_size[1] % 2 == 1:
        kpes = (np.arange(0, matrix_size[1], 1) - np.floor(matrix_size[1] / 2)) * delta_kpe
    else:
        kpes = (np.arange(0, matrix_size[1], 1) - (matrix_size[1] + 1) // 2) * delta_kpe

    # Figure out prephaser shortest prephaser duration for maximal k-space traverse
    prephaser_duration = kwargs.get("prephaser_duration", None)
    if prephaser_duration is None:
        seq_max = fnc(system_specs, num_samples=matrix_size[0], k_phase=kpes[0], k_readout=kro_max,
                      **kwargs)
        prephaser_block = seq_max.get_block("ro_prephaser_0")
        prephaser_duration = system_specs.time_to_raster(prephaser_block.duration)
        kwargs["prephaser_duration"] = prephaser_duration
    sequence_list = []
    # Add dummy shots
    if dummy_shots is not None:
        dummy = fnc(system_specs, num_samples=0, k_readout=kro_max,
                    k_phase=0 * delta_kpe, **kwargs)
        for _ in range(dummy_shots):
            sequence_list.append(deepcopy(dummy))

    for kpe in kpes:
        seq = fnc(system_specs, num_samples=matrix_size[0], k_readout=kro_max,
                  k_phase=kpe, **kwargs)
        sequence_list.append(seq)
    return sequence_list


# pylint: disable=W1401, R0913, R0914
def gre_cartesian_line(system_specs: cmrseq.SystemSpec,
                       num_samples: int,
                       k_readout: Quantity,
                       k_phase: Quantity,
                       adc_duration: Quantity,
                       delay: Quantity = Quantity(0., "ms"),
                       prephaser_duration: Quantity = None) -> cmrseq.Sequence:
    """Generates a gradient sequence to apply phase encoding (0, 1.,0.) direction and a readout
    including adc-events for a single line in gradient direction (1., 0., 0.). Is designed to work
    for gradient-echo based readouts.

    .. code-block:: python

       . ADC:                      ||||||     -> num_samples    .
       .                           ______                       .
       . RO:      ___________     /      \                      .
       .                     \___/                              .
       .                      ___                               .
       . PE:      ___________/   \________                      .
       .                                                        .
       .         | delay    |     |     |                       .
       .                        adc_duration                    .

    :param system_specs: SystemSpecification
    :param num_samples: Number of samples acquired during frequency encoding
    :param k_readout: Quantity[1/Length] :math:`FOV_{kx}` corresponds to :math:`1/\Delta x`   s
    :param k_phase: Quantity[1/Length] :math:`n \Delta k_{y}` phase encoding strength of
                        current line
    :param adc_duration: Quantity[time] Total duration of adc-sampling for a single TR
    :param delay:
    :param prephaser_duration: Optional - if not specified the shortest possible duration for the
                                RO/PE prephaser is calculates
    :return: Sequence object containing RO- & PE-gradients as well as ADC events
    """
    adc_duration = system_specs.time_to_raster(adc_duration, raster="grad")

    ro_amp = (k_readout / adc_duration / system_specs.gamma).to("mT/m")
    readout_pulse = cmrseq.bausteine.TrapezoidalGradient.from_fdur_amp(
        system_specs=system_specs,
        orientation=np.array([1., 0., 0.]),
        flat_duration=adc_duration,
        amplitude=ro_amp, delay=Quantity(0., "ms"),
        name="trapezoidal_readout"
    )

    prephaser_ro_area = readout_pulse.area[0] / 2.
    prephaser_pe_area = np.abs(k_phase / system_specs.gamma)

    # Total gradient traverse is a combination of ro and pe directions.
    # Need to solve as single gradient to ensure slew and strength restrictions are met
    combined_kspace_traverse = np.sqrt((prephaser_ro_area * system_specs.gamma) ** 2 + k_phase ** 2)
    [_, fastest_prep_ramp, fastest_prep_flatdur] = system_specs.get_shortest_gradient(
        combined_kspace_traverse / system_specs.gamma)

    # If prephaser duration was not specified use the fastest posible prephaser
    if prephaser_duration is None:
        prephaser_duration = fastest_prep_flatdur + 2 * fastest_prep_ramp
    else:
        # Check if duration is sufficient for _combined_ prephaser gradients
        if prephaser_duration < np.round(fastest_prep_flatdur + 2 * fastest_prep_ramp, 7):
            raise ValueError("Prephaser duration is to short for combined PE+RO k-space traverse.")

    readout_pulse.shift(prephaser_duration + delay)
    ro_prep_pulse = cmrseq.bausteine.TrapezoidalGradient.from_dur_area(
        system_specs=system_specs,
        orientation=np.array([-1., 0., 0.]),
        duration=prephaser_duration,
        area=prephaser_ro_area,
        delay=delay, name="ro_prephaser")

    pe_direction = np.array([0., 1., 0.]) * np.sign(k_phase)
    pe_prep_pulse = cmrseq.bausteine.TrapezoidalGradient.from_dur_area(
        system_specs=system_specs,
        orientation=pe_direction,
        duration=prephaser_duration,
        area=prephaser_pe_area,
        delay=delay, name="pe_prephaser")

    if num_samples > 0:
        adc = cmrseq.bausteine.SymmetricADC(system_specs=system_specs, num_samples=num_samples,
                                            duration=adc_duration,
                                            delay=prephaser_duration + delay + readout_pulse.rise_time)
        return cmrseq.Sequence([ro_prep_pulse, pe_prep_pulse, readout_pulse, adc],
                               system_specs=system_specs)
    else:
        return cmrseq.Sequence([ro_prep_pulse, pe_prep_pulse, readout_pulse],
                               system_specs=system_specs)


# pylint: disable=W1401, R0913, R0914
def balanced_gre_cartesian_line(system_specs: cmrseq.SystemSpec,
                                num_samples: int,
                                k_readout: Quantity,
                                k_phase: Quantity,
                                adc_duration: Quantity,
                                delay: Quantity = Quantity(0., "ms"),
                                prephaser_duration: Quantity = None) -> cmrseq.Sequence:
    """ Generates a gradient sequence to apply phase encoding (0, 1.,0.) direction and a readout
    including adc-events for a single line in gradient direction (1., 0., 0.). After readout
    prephasers are rewound. Is designed to work for gradient-echo based readouts.

    .. code-block: python

       .        ADC:                      ||||||     -> num_samples        .
       .                                  ______                           .
       .        RO:      ___________     /      \     ______               .
       .                            \___/        \___/                     .
       .                             ___          ___                      .
       .        PE:      ___________/   \________/   \_____                .
       .                                                                   .
       .                | delay    |     |     |                           .
       .                              adc_duration                         .

    :param system_specs: SystemSpecification
    :param num_samples: Number of samples acquired during frequency encoding
    :param k_readout: Quantity[1/Length] :math:`FOV_{kx}` corresponds to :math:`1/\Delta x`   s
    :param k_phase: Quantity[1/Length] :math:`n \Delta k_{y}` phase encoding
                        strength of current line
    :param adc_duration: Quantity[time] Total duration of adc-sampling for a single TR
    :param delay:
    :param prephaser_duration: Optional - if not specified the shortest possible duration for the
                                RO/PE prephaser is calculates
    :return: Sequence object containing RO- & PE-gradients plus rewinders as well as ADC events
    """
    seq = gre_cartesian_line(system_specs=system_specs, num_samples=num_samples,
                             k_readout=k_readout, k_phase=k_phase,
                             adc_duration=adc_duration, delay=delay,
                             prephaser_duration=prephaser_duration)
    # Copy prephasers
    prep_ro_block = deepcopy(seq.get_block("ro_prephaser_0"))
    prep_pe_block = deepcopy(seq.get_block("pe_prephaser_0"))

    # Shift to end of readout
    ro_duration = seq["trapezoidal_readout_0"].duration
    prep_pe_block.shift(ro_duration + prep_pe_block.duration)
    prep_ro_block.shift(ro_duration + prep_ro_block.duration)

    # Invert amplidute
    prep_pe_block.scale_gradients(-1)

    prep_pe_block.name = "pe_prephaser_balance"
    prep_ro_block.name = "ro_prephaser_balance"

    seq += cmrseq.Sequence([prep_ro_block, prep_pe_block], system_specs=system_specs)
    return seq


# pylint: disable=W1401, R0913, R0914
def se_cartesian_line(system_specs: cmrseq.SystemSpec,
                      num_samples: int,
                      echo_time: Quantity,
                      pulse_duration: Quantity,
                      excitation_center_time: Quantity,
                      k_readout: Quantity,
                      k_phase: Quantity,
                      adc_duration: Quantity,
                      delay: Quantity = Quantity(0., "ms"),
                      prephaser_duration: Quantity = None) -> cmrseq.Sequence:
    """ Generates a gradient sequence to apply phase encoding (0, 1.,0.) direction and a readout
    including adc-events for a single line in gradient direction (1., 0., 0.) for a spin-echo based
    readout.

    .. code-block:: python

        .                excitation center                                  .
        .                   |                                               .
        .                   |   TE/2 |   TE/2 |                             .
        .   ADC:                           ||||||     -> num_samples        .
        .                      ___         ______                           .
        .   RO:           ____/   \_______/      \                          .
        .                      ___                                          .
        .   PE:           ____/   \_____________                            .
        .           |   |                 |     |                           .
        .           delay              adc_duration                         .
        .               |    |                                              .
        .           pulse_duration                                          .


    :raises ValueError: If phase/frequency encoding amplitude would exceed system limits

    :param system_specs: SystemSpecification
    :param num_samples: Number of samples acquired during frequency encoding
    :param echo_time:
    :param pulse_duration: total time of ss-gradient (including ramps)
    :param excitation_center_time: Quantity[Time] Reference time-point to calculate TE from
    :param k_readout: Quantity[1/Length] :math:`FOV_{kx}` corresponds to :math:`1/\Delta x`
    :param k_phase: Quantity[1/Length] :math:`n \Delta k_{y}` phase encoding
                            strength of current line
    :param adc_duration: Quantity[time] Total duration of adc-sampling for a single TR
    :param prephaser_duration: Optional - if not specified the shortest possible duration for the
                                RO/PE prephaser is calculates
    :return: Sequence containing the RO/PE prephaser, RO and adc events for a spin-echo read-out
    """

    ro_amp = (k_readout / adc_duration / system_specs.gamma).to("mT/m")
    rise_time = system_specs.get_shortest_rise_time(ro_amp)
    if adc_duration >= (echo_time / 2 - rise_time - pulse_duration / 2) * 2:
        raise ValueError("Specified ADC-duration is larger than available time from "
                         "end of refocusing pulse to Echo center")

    ro_delay = delay + excitation_center_time + echo_time - adc_duration / 2
    readout_pulse = cmrseq.bausteine.TrapezoidalGradient.from_fdur_amp(
        system_specs=system_specs,
        orientation=np.array([1., 0., 0.]),
        flat_duration=adc_duration,
        amplitude=ro_amp, delay=ro_delay,
        name="readout_grad")
    readout_pulse.shift(-readout_pulse.rise_time)
    prephaser_ro_area = readout_pulse.area[0] / 2.
    prephaser_pe_area = np.abs(k_phase / system_specs.gamma)

    # Total gradient traverse is a combination of ro and pe directions.
    # Need to solve as single gradient to ensure slew and strength restrictions are met
    combined_kspace_traverse = np.sqrt((prephaser_ro_area * system_specs.gamma) ** 2 + k_phase ** 2)
    [_, fastest_prep_ramp, fastest_prep_flatdur] = system_specs.get_shortest_gradient(
        combined_kspace_traverse / system_specs.gamma)

    # If prephaser duration was not specified use the fastest possible prephaser
    if prephaser_duration is None:
        prephaser_duration = fastest_prep_flatdur + 2 * fastest_prep_ramp
    else:
        if prephaser_duration < fastest_prep_flatdur + 2 * fastest_prep_ramp:
            raise ValueError("Prephaser duration is to short to for combined PE+RO "
                             "k-space traverse.")

    prephaser_delay = delay + echo_time / 2 - pulse_duration / 2 \
                      - prephaser_duration + excitation_center_time
    ro_prep_pulse = cmrseq.bausteine.TrapezoidalGradient.from_dur_area(
        system_specs=system_specs,
        orientation=np.array([1., 0., 0.]),
        duration=prephaser_duration,
        area=prephaser_ro_area,
        delay=prephaser_delay,
        name="ro_prephaser")

    pe_direction = np.array([0., -1., 0.]) * np.sign(k_phase)
    pe_prep_pulse = cmrseq.bausteine.TrapezoidalGradient.from_dur_area(system_specs=system_specs,
                                                                       orientation=pe_direction,
                                                                       duration=prephaser_duration,
                                                                       area=prephaser_pe_area,
                                                                       delay=prephaser_delay,
                                                                       name="pe_prephaser")
    adc_delay = readout_pulse.tmin + readout_pulse.rise_time
    adc = cmrseq.bausteine.SymmetricADC(system_specs=system_specs, num_samples=num_samples,
                                        duration=adc_duration,
                                        delay=adc_delay)
    return cmrseq.Sequence([ro_prep_pulse, pe_prep_pulse, readout_pulse, adc],
                           system_specs=system_specs)
