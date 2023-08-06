__all__ = ["balanced_ssfp", "radial_balanced_ssfp"]

from typing import Tuple, List
from copy import deepcopy
from warnings import warn

import numpy as np
from pint import Quantity

import cmrseq


def balanced_ssfp(system_specs: cmrseq.SystemSpec,
                  matrix_size: np.ndarray,
                  inplane_resolution: Quantity,
                  slice_thickness: Quantity,
                  adc_duration: Quantity,
                  flip_angle: Quantity,
                  pulse_duration: Quantity,
                  repetition_time: Quantity,
                  slice_position_offset: Quantity = Quantity(0., "m"),
                  time_bandwidth_product: float = 4.,
                  dummy_shots: int = None,
                  fuse_slice_rewind_and_prephaser: bool = True) -> List[cmrseq.Sequence]:
    """ Defines a balanced steady state free precession sequence with a/2-TR/2 preparation.

    Signle TR defintition:

    .. code-block::

        .                 |                  TR                  |                 .
        .                     |       TE         |                                 .
        .                                                                          .
        .            RF:     /\                                                    .
        .            ADC   \/  \/      |||||||||||||||||||||                       .
        .                  ______                                                  .
        .            SS:  /      \    _______________________                      .
        .                         \__/                       \__/                  .
        .                              _____________________                       .
        .            RO:  ________    /                     \                      .
        .                         \__/                       \__/                  .
        .                                                    __                    .
        .            PE:  ________    ______________________/  \                   .
        .                         \__/                                             .


    :param system_specs: SystemSpecification
    :param matrix_size: array of shape (2, )
    :param inplane_resolution: Quantity[Length] of shape (2, )
    :param repetition_time: Quantity[Time] containing the required repetition_time
    :param slice_thickness: Quantity[Length] containing the required slice-thickness
    :param adc_duration: Quantity[time] Total duration of adc-sampling for a single TR
    :param flip_angle: Quantity[Angle] containing the required flip_angle
    :param pulse_duration: Quantity[Time] Total pulse duration (corresponds to flat_duration of the
                            slice selection gradient)
    :param slice_position_offset: Quantity[Length] positional offset in slice normal direction
                              defining the frequency offset of the RF pulse
    :param time_bandwidth_product: float - used to calculate the rf bandwidth from duration
    :param dummy_shots: number of shots(TRs) without adc-events before starting the acquisition
    :param fuse_slice_rewind_and_prephaser: If True, the slice selection rewinder is recalculated
            to match the duration of the prephaser, resulting in the fastest possible 3D k-space
            traverse.
    :return: List of length (n_dummy+matrix_size[1]) containting one Sequence object per TR
    """
    rf_seq = cmrseq.seqdefs.excitation.slice_selective_sinc_pulse(
                                    system_specs=system_specs,
                                    slice_thickness=slice_thickness,
                                    flip_angle=flip_angle/2,
                                    pulse_duration=pulse_duration,
                                    time_bandwidth_product=time_bandwidth_product,
                                    slice_position_offset=slice_position_offset,
                                    slice_normal=np.array([0., 0., 1.]))
    ss_refocus = rf_seq.get_block("slice_select_rewind_0")

    if fuse_slice_rewind_and_prephaser:
        # Recalculate ss-gradient combined with ro/pe prephasers
        k_max_inplane = 1 / (2 * inplane_resolution.m_as("m"))
        kz_refocus = (ss_refocus.area * system_specs.gamma).m_as("1/m")
        total_kspace_traverse = Quantity(np.linalg.norm([*k_max_inplane, kz_refocus[-1]]), "1/m")
        combined_gradient_area = total_kspace_traverse / system_specs.gamma.to("1/mT/ms")
        prephaser_duration = cmrseq.bausteine.TrapezoidalGradient.from_area(
                                system_specs, np.array([1., 0., 0]), combined_gradient_area).duration
        rf_seq.remove_block("slice_select_rewind_0")

        rf_seq.append(cmrseq.bausteine.TrapezoidalGradient.from_dur_area(system_specs,
                                                                         np.array([0., 0., -1.]),
                                                                         prephaser_duration,
                                                                         ss_refocus.area[-1],
                                                                         name="slice_select_rewind"))
        ss_refocus = rf_seq.get_block("slice_select_rewind_0")
    else:
        prephaser_duration = None

    # Construct the readout and phase encoding gradients
    ro_blocks = cmrseq.seqdefs.readout.multi_line_cartesian(
                                    system_specs=system_specs,
                                    fnc=cmrseq.seqdefs.readout.balanced_gre_cartesian_line,
                                    matrix_size=matrix_size,
                                    inplane_resolution=inplane_resolution,
                                    adc_duration=adc_duration,
                                    prephaser_duration=prephaser_duration,
                                    dummy_shots=dummy_shots)

    if prephaser_duration is None:
        prephaser_duration = ro_blocks[-1].get_block("ro_prephaser_0").duration

    # Create the slice selection compensation
    ss_compensate = deepcopy(ss_refocus)
    ss_compensate.name = "slice_select_prewind"

    # Adjust alternating phase offset for adc-events
    for ro_idx, ro_b in enumerate(ro_blocks):
        phase_offset = Quantity(np.mod(ro_idx, 2) * np.pi, "rad")
        adc_block = ro_b.get_block("adc_0")
        if adc_block is not None:
            adc_block.phase_offset = phase_offset

    # Calculate minimum allowable TR
    readout_gradient_duration = ro_blocks[-1].get_block("trapezoidal_readout_0").duration
    max_ssref_prephaser = max(ss_refocus.duration, prephaser_duration)
    if fuse_slice_rewind_and_prephaser:
        minimal_tr = readout_gradient_duration + 2 * max_ssref_prephaser + rf_seq.duration - ss_refocus.duration
    else:
        minimal_tr = ro_blocks[-1].duration + rf_seq.duration + ss_compensate.duration

    # Warn if repetition time is too short
    repetition_time = system_specs.time_to_raster(repetition_time)
    if repetition_time < minimal_tr:
        warn(f"Repetition time too short to be feasible, set TR to {minimal_tr}")
        repetition_time = minimal_tr

    tr_delay_half = system_specs.time_to_raster((repetition_time - minimal_tr)/2)

    ss_compensate.shift(-ss_compensate.tmin + repetition_time - ss_compensate.duration)

    # Add delay to match TR/2 after the first exication
    rf_seq.append(cmrseq.bausteine.Delay(system_specs, repetition_time/2 - rf_seq.duration))

    # Assemble blocks to list of sequences each representing one TR
    seq_list = [rf_seq]
    for tr_idx, ro_b in enumerate(ro_blocks):
        flip_angle_phase = (-1) ** tr_idx * flip_angle
        rf_seq = cmrseq.seqdefs.excitation.slice_selective_sinc_pulse(
                                                    system_specs=system_specs,
                                                    slice_thickness=slice_thickness,
                                                    flip_angle=flip_angle_phase,
                                                    pulse_duration=pulse_duration,
                                                    slice_position_offset=slice_position_offset,
                                                    time_bandwidth_product=time_bandwidth_product,
                                                    slice_normal=np.array([0., 0., 1.]))
        if fuse_slice_rewind_and_prephaser:
            rf_seq.remove_block("slice_select_rewind_0")
            rf_seq.append(cmrseq.bausteine.TrapezoidalGradient.from_dur_area(system_specs,
                                                                             np.array([0., 0., -1.]),
                                                                             prephaser_duration,
                                                                             ss_refocus.area[-1],
                                                                             name="slice_select_rewind"))
        if fuse_slice_rewind_and_prephaser:
            ro_b.shift_in_time(
                rf_seq.duration - min(ss_refocus.duration, prephaser_duration)+tr_delay_half)
        else:
            ro_b.shift_in_time(
                rf_seq.duration + tr_delay_half)

        seq = rf_seq + ro_b + cmrseq.Sequence([ss_compensate, ], system_specs)
        seq_list.append(seq)
    return seq_list


def radial_balanced_ssfp(system_specs: cmrseq.SystemSpec,
                         samples_per_spoke: int,
                         inplane_resolution: Quantity,
                         slice_thickness: Quantity,
                         adc_duration: Quantity,
                         flip_angle: Quantity,
                         pulse_duration: Quantity,
                         repetition_time: Quantity,
                         spoke_angle_increment: Quantity = None,
                         num_spokes: int = None,
                         slice_position_offset: Quantity = Quantity(0., "m"),
                         time_bandwidth_product: float = 4.,
                         dummy_shots: int = 0,
                         fuse_slice_rewind_and_prephaser: bool = True) -> List[cmrseq.Sequence]:

    rf_seq = cmrseq.seqdefs.excitation.slice_selective_sinc_pulse(
        system_specs=system_specs,
        slice_thickness=slice_thickness,
        flip_angle=flip_angle,
        pulse_duration=pulse_duration,
        time_bandwidth_product=time_bandwidth_product,
        slice_position_offset=slice_position_offset,
        slice_normal=np.array([0., 0., 1.]))
    ss_refocus = rf_seq.get_block("slice_select_rewind_0")

    kr_max = 1 / (2 * inplane_resolution.m_as("m"))

    if fuse_slice_rewind_and_prephaser:
        # Recalculate ss-gradient combined with ro prephaser

        kz_refocus = (ss_refocus.area * system_specs.gamma).m_as("1/m")

        total_kspace_traverse = Quantity(np.linalg.norm([kr_max, kz_refocus[-1]]), "1/m")
        combined_gradient_area = total_kspace_traverse / system_specs.gamma.to("1/mT/ms")
        prephaser_duration = cmrseq.bausteine.TrapezoidalGradient.from_area(
            system_specs, np.array([1., 0., 0]), combined_gradient_area).duration

        rf_seq.remove_block("slice_select_rewind_0")
        ss_refocus = cmrseq.bausteine.TrapezoidalGradient.from_dur_area(system_specs,
                                                                        np.array([0., 0., -1.]),
                                                                        prephaser_duration,
                                                                        ss_refocus.area[-1],
                                                                        delay=rf_seq.duration,
                                                                        name="slice_select_rewind")
        rf_seq.add_block(ss_refocus)
    else:
        prephaser_duration = None

    ro_ref = cmrseq.seqdefs.readout.balanced_radial_spoke(system_specs=system_specs, num_samples=samples_per_spoke,
                                                          kr_max=Quantity(kr_max, '1/m'), angle=Quantity(0, 'rad'),
                                                          adc_duration=adc_duration,
                                                          prephaser_duration=prephaser_duration)

    dummy_ref = cmrseq.seqdefs.readout.balanced_radial_spoke(system_specs=system_specs, num_samples=0,
                                                             kr_max=Quantity(kr_max, '1/m'), angle=Quantity(0, 'rad'),
                                                             adc_duration=adc_duration,
                                                             prephaser_duration=prephaser_duration)

    if prephaser_duration is None:
        prephaser_duration = ro_ref.get_block("radial_prephaser_0").duration


    # Create the slice selection compensation
    ss_compensate = deepcopy(ss_refocus)
    ss_compensate.name = "slice_select_prewind"


    readout_gradient_duration = ro_ref.get_block("radial_readout_0").duration
    max_ssref_prephaser = max(ss_refocus.duration, prephaser_duration)

    if fuse_slice_rewind_and_prephaser:
        minimal_tr = readout_gradient_duration + 2 * max_ssref_prephaser + rf_seq.duration - ss_refocus.duration
    else:
        minimal_tr = ro_ref.duration + rf_seq.duration + ss_compensate.duration

    repetition_time = system_specs.time_to_raster(repetition_time)
    if repetition_time < minimal_tr:
        warn(f"Repetition time too short to be feasible, set TR to {minimal_tr}")
        repetition_time = minimal_tr


    tr_delay_half = system_specs.time_to_raster((repetition_time - minimal_tr)/2)

    ss_compensate.shift_time(-ss_compensate.tmin+ repetition_time - ss_compensate.duration)

    # Generate catalyst with TR/2 duration
    rf_catalyst= deepcopy(rf_seq)
    rf_catalyst.append(cmrseq.bausteine.Delay(system_specs, repetition_time / 2 - rf_seq.duration))

    # Concatenate readout blocks
    seq_list = [rf_catalyst]

    # Start with dummy shots
    for idx in range(dummy_shots):
        # Alternating RF pulse phase
        flip_angle_phase = (-1) ** (idx+1) * flip_angle
        rf_seq = cmrseq.seqdefs.excitation.slice_selective_sinc_pulse(
                                                    system_specs=system_specs,
                                                    slice_thickness=slice_thickness,
                                                    flip_angle=flip_angle_phase,
                                                    pulse_duration=pulse_duration,
                                                    slice_position_offset=slice_position_offset,
                                                    time_bandwidth_product=time_bandwidth_product,
                                                    slice_normal=np.array([0., 0., 1.]))
        rf_seq.remove_block("slice_select_rewind_0")
        rf_seq.append(cmrseq.bausteine.TrapezoidalGradient.from_dur_area(system_specs,
                                                                         np.array([0., 0., -1.]),
                                                                         prephaser_duration,
                                                                         ss_refocus.area[-1],
                                                                         name="slice_select_rewind"))

        cur_ro = deepcopy(dummy_ref)
        if fuse_slice_rewind_and_prephaser:
            cur_ro.shift_in_time(
                rf_seq.duration - min(ss_refocus.duration, prephaser_duration)+tr_delay_half)
        else:
            cur_ro.shift_in_time(
                rf_seq.duration + tr_delay_half)
        seq = rf_seq + cur_ro + cmrseq.Sequence([ss_compensate, ], system_specs)
        seq_list.append(seq)

    # Calculate angle increment scheme
    if num_spokes is None:
        if spoke_angle_increment is not None:
            warn(f"Can not set spoke angle increment without setting number of spokes, defaulting to satisfy nyquist")

        num_spokes = np.ceil(samples_per_spoke*np.pi/2) # Nyquist criteria for radial sampling

        spoke_angles = np.linspace(0,np.pi,int(num_spokes), endpoint=False)
    else:
        if spoke_angle_increment is None:
            warn(f"Spoke angle not set while spoke count set, defaulting to even spacing of spokes")
            spoke_angles = np.linspace(0,np.pi,int(num_spokes), endpoint=False)
        else:
            spoke_angles = np.array(range(num_spokes))*spoke_angle_increment.to('rad').m_as('dimensionless')

    # Readout shots
    for angle,idx in zip(spoke_angles,range(len(spoke_angles))):
        # Alternating RF pulse phase
        flip_angle_phase = (-1) ** (idx + dummy_shots + 1) * flip_angle
        rf_seq = cmrseq.seqdefs.excitation.slice_selective_sinc_pulse(
            system_specs=system_specs,
            slice_thickness=slice_thickness,
            flip_angle=flip_angle_phase,
            pulse_duration=pulse_duration,
            slice_position_offset=slice_position_offset,
            time_bandwidth_product=time_bandwidth_product,
            slice_normal=np.array([0., 0., 1.]))
        if fuse_slice_rewind_and_prephaser:
            rf_seq.remove_block("slice_select_rewind_0")
            rf_seq.append(cmrseq.bausteine.TrapezoidalGradient.from_dur_area(system_specs,
                                                                             np.array([0., 0., -1.]),
                                                                             prephaser_duration,
                                                                             ss_refocus.area[-1],
                                                                             name="slice_select_rewind"))

        cur_ro = deepcopy(ro_ref)
        sa = np.sin(angle)
        ca = np.cos(angle)
        R = np.array([[ca, -sa, 0], [sa, ca, 0], [0, 0, 1]])

        cur_ro.rotate_gradients(R)
        if fuse_slice_rewind_and_prephaser:
            cur_ro.shift_in_time(
                rf_seq.duration - min(ss_refocus.duration, prephaser_duration)+tr_delay_half)
        else:
            cur_ro.shift_in_time(
                rf_seq.duration + tr_delay_half)

        # Adjust alternating phase offset for adc-events
        phase_offset = Quantity(np.mod(idx + dummy_shots + 1, 2) * np.pi, "rad")
        adc_block = cur_ro.get_block("adc_0")
        if adc_block is not None:
            adc_block.phase_offset = phase_offset

        seq = rf_seq + cur_ro + cmrseq.Sequence([ss_compensate, ], system_specs)
        seq_list.append(seq)

    return seq_list