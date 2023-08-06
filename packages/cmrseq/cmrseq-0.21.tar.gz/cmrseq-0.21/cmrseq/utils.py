"""This module contains re-occurring functionality, that is semantically not bound to the classes
defined in the cmrseq package"""
__all__ = ["mps_to_xyz", "get_rotation_matrix", "get_partial_sequence", "grid_sequence_list",
           "calculate_diffusion_weighting", "calculate_gradient_spectra"]

from typing import Iterable, List, Tuple
from copy import deepcopy

from pint import Quantity
import numpy as np
import scipy.integrate

from cmrseq import Sequence


def mps_to_xyz(gradients: np.ndarray, slice_normal: np.ndarray = np.array([1., 0., 0.]),
               readout_direction : np.ndarray = np.array([0., 0., 1.])) -> np.ndarray:
    """ Converts from MPS formalism to scanner coordinates XYZ. Default scheme is Coronal slice
     with measurement in Z If M and S are not orthogonal, M is adjusted.

    :param gradients: (..., 3) np.array containing gradient waveforms defined in MPS coordinates
    :param slice_normal: np.array (3, ) containing the slice orientation in XYZ coordinates
    :param readout_direction: np.array (3, ) containing the readout direction in XYZ coordinates
    :return: (..., 3) rotated gradient waveform in XYZ coordinates
    """
    rotation_matrix = get_rotation_matrix(slice_normal, readout_direction, target_orientation="xyz")
    return np.einsum('ij,...j->...i', rotation_matrix, gradients)


def xyz_to_mps(gradients: np.ndarray, slice_normal: np.ndarray = np.array([1., 0., 0.]),
               readout_direction: np.ndarray = np.array([0., 0., 1.])) -> np.ndarray:
    """ Converts from XYZ formalism to scanner coordinates MPS. Default scheme is Coronal slice
     with measurement in Z If M and S are not orthogonal, M is adjusted.

    :param gradients: (..., 3) np.array containing gradient waveforms defined in XYZ coordinates
    :param slice_normal: np.array (3, ) containing the slice orientation in XYZ coordinates
    :param readout_direction: np.array (3, ) containing the readout direction in XYZ coordinates
    :return: (..., 3) rotated gradient waveform in MPS coordinates
    """
    rotation_matrix = get_rotation_matrix(slice_normal, readout_direction, target_orientation="mps")
    return np.einsum('ij,...j->...i', rotation_matrix, gradients)


def get_rotation_matrix(slice_normal: np.ndarray,
                        readout_direction: np.ndarray,
                        target_orientation: str = "xyz") -> np.ndarray:
    """ Evaluates a rotation matrix according which can be used to transform between
    MPS and XYZ coordinates.
    If M and S are not orthogonal, M is adjusted.

    :param slice_normal: Slice normal vector in XYZ coordinates
    :param readout_direction: Readout vector in XYZ coordinates
    :param target_orientation: str, either ('mps', 'xyz')
    :return: (3, 3) array the 0th axis indexes the M/P/S vector in cartesian coordinates

        - M = R[0, :]
        - P = R[1, :]
        - S = R[2, :]
    """
    readout_direction = readout_direction / np.linalg.norm(readout_direction)
    slice_normal = slice_normal / np.linalg.norm(slice_normal)
    phase_direction = np.cross(slice_normal, readout_direction)
    phase_direction = phase_direction / np.linalg.norm(phase_direction)

    if np.dot(slice_normal, readout_direction) != 0:
        readout_direction = np.cross(phase_direction, slice_normal)
        readout_direction = readout_direction / np.linalg.norm(readout_direction)

    rot_to_xyz = np.stack([readout_direction, phase_direction, slice_normal], axis=0)
    if target_orientation.lower() == "xyz":
        rot_mat = rot_to_xyz
    elif target_orientation.lower() == "mps":
        rot_mat = np.linalg.inv(rot_to_xyz)
    else:
        raise ValueError("Target direction not valid! Expected one of ['xyz', 'mps'] "
                         f"but got: {target_orientation}")
    return rot_mat


def get_partial_sequence(seq: 'Sequence', block_names: Iterable[str], copy: bool = True):
    """ For an Iterable of block-names, gets the blocks from given sequence and creates a new
    sequence object from it. If `copy` is True, the blocks are copy on creating the new Sequence
    object.

    :param seq: Sequence object from which the blocks are extracted
    :param block_names: Iterable of strings denoting the blocks to be extracted from Sequence
    :param copy: if True every extracted block is deepcopied
    :return: Sequence Object
    """
    name_in_sequence = [bn in seq.blocks for bn in block_names]
    if not all(name_in_sequence):
        missing_blocks = [block_names[i] for i, _ in enumerate(name_in_sequence) if not _]
        raise ValueError(f"Specified blocks {missing_blocks} not present in {seq.blocks}")

    if copy:
        extracted_blocks = [deepcopy(seq.get_block(bn)) for bn in block_names]
    else:
        extracted_blocks = [seq.get_block(bn) for bn in block_names]

    new_sequence = Sequence(extracted_blocks, system_specs=seq._system_specs)  # pylint: disable=W0212
    return new_sequence


# pylint: disable=C0103
def grid_sequence_list(sequence_list: List[Sequence],
                       force_uniform_grid: bool = False) \
        -> Tuple[List[np.ndarray], ...]:
    """ Grids RF, Gradients and adc_events of all sequences in the provided List.

    :param sequence_list:
    :param force_uniform_grid: bool if False the ADC-events are inserted into the time grid
                resulting in a non-uniform raster per TR
    :return: (time, rf_list, wf_list, adc_list)
    """
    time_list, rf_list, grad_list, adc_list = [], [], [], []
    for seq in sequence_list:
        rf, wf, adc_info = None, None, None
        if len(seq.rf) > 0:
            time_rf, rf = seq.rf_to_grid()
            time = time_rf
        if len(seq.gradients) > 0:
            time_grad, wf = seq.gradients_to_grid()
            wf = wf.T
            time = time_grad
        if len(seq.adc_centers) > 0:
            t_adc, adc_on, adc_phase, start_end = seq.adc_to_grid(force_raster=force_uniform_grid)
            adc_info = np.stack([adc_on, adc_phase], axis=-1)

        if 'start_end' in locals():
            if force_uniform_grid:
                adc_on[start_end[0, 0]:start_end[0, 1]] = 1
            else:
                if len(seq.gradients) > 0:
                    wf = np.stack([np.interp(t_adc, time_grad, g) for g in wf.T], axis=-1)
                if len(seq.rf) > 0:
                    rf = np.interp(t_adc, time_rf, rf)
                time = t_adc

        rf_list.append(rf)
        grad_list.append(wf)
        adc_list.append(adc_info)
        time_list.append(time)

    return time_list, rf_list, grad_list, adc_list


def calculate_diffusion_weighting(seq: Sequence, return_bmatrix: bool = False,
                                  return_cumulative: bool = False):
    """Evaluates the b-value or b-matrix of arbitrary gradient waveforms by numerical integration.

    :param seq: Sequence object, which is gridded to obtain hte waveform
    :param return_bmatrix: If True returns the b-matrix instead of the scalar b-value
    :param return_cumulative: if True returns the bvalue on raster-time resolution
    :return: Quantity of shape (1, ) or (t, ) depending on `return_cumulative` argument
    """
    time, gradient_waveform = seq.gradients_to_grid()

    # Integrate the waveform to obtain the zeroth oder moment at all times
    gradient_moment = scipy.integrate.cumulative_trapezoid(gradient_waveform, x=time,
                                                           initial=True, axis=1)
    q_of_t = (Quantity(gradient_moment, "mT/m*ms") * seq._system_specs.gamma_rad).to("1/mm")

    # compute the dot product per time step to obtain the squared gradient moment
    q_squared = Quantity(np.einsum('it, jt -> ijt', q_of_t.m_as("1/mm"), q_of_t.m_as("1/mm")),
                         "1/mm**2")
    q_squared = q_squared.reshape(9, -1)

    if return_cumulative:
        b_val_unitless = scipy.integrate.cumulative_trapezoid(q_squared.m, x=time, initial=True,
                                                              axis=-1)
    else:
        b_val_unitless = scipy.integrate.trapz(q_squared.m, x=time, axis=-1)

    if not return_bmatrix:
        b_val_unitless = np.trace(b_val_unitless.reshape(3, 3, -1), axis1=0, axis2=1)
    bvals = Quantity(b_val_unitless, f"{q_squared.units} * ms")
    return bvals.to("s/mm**2")

def calculate_gradient_spectra(sequence: Sequence,
                               directions: List[np.ndarray],
                               start_time: Quantity = None,
                               end_time: Quantity = None,
                               interpolation_subfactor: int = 1,
                               pad_factor: int = 10):
    """ Calculates gradient sampling spectra along a given direction according to:

    .. math::

        S(\\omega,t) = |\\tilde{q}(\\omega,t)|^2

        \\tilde{q}(\\omega,t) = \\int_{0}^{t}q(t')e^{i\\omega t'}dt'

        q(t) = \\gamma \\int_{0}^{t}G(t')dt'

    where G(t) is the gradient. Spectra returns in units of :math:`mT^2/m^2/ms^4`

    :param sequence: Sequence to calculate spectra on
    :param directions: List[np.ndarray of shape (3, )] denoting the directions to calculate spectra along
    :param start_time: Quantity[Time] Start time of spectra calculation window
    :param end_time: Quantity[Time] End time of spectra calculation window
    :param interpolation_subfactor: int, factor to divide sequence raster time by for spectra calculation
    :param pad_factor: int, multiplicative pad factor prior to fourier transform. Used to better resolve low frequencies
    :return: (List[Spectra],Frequency) Tuple of arrays giving spectra and frequency axis
    """

    seq = deepcopy(sequence)

    # In some cases we want finer gradient raster in order to produce smoother/better resolved spectra
    if interpolation_subfactor > 1: interpolation_subfactor = 1
    seq._system_specs.grad_raster_time = seq._system_specs.grad_raster_time / interpolation_subfactor

    # normalize direction
    # direction = direction / np.linalg.norm(direction)

    # get gradients
    time, gradients = seq.gradients_to_grid()

    # project along dimension
    # gradients = np.sum((gradients * np.expand_dims(direction, 1)), axis=0))

    # MPS directions
    gm = gradients[0]
    gp = gradients[1]
    gs = gradients[2]

    # Get start and end indices
    if end_time is None:
        end_ind = -1
    else:
        end_ind = np.argmin(np.abs(time - end_time.m_as('ms'))) + 1

    if start_time is None:
        start_ind = 0
    else:
        start_ind = np.argmin(np.abs(time - start_time.m_as('ms')))

    # Perform spectra calculation of MPS directions as a basis
    # M
    qtm = np.cumsum(gm[start_ind:end_ind]) * seq._system_specs.grad_raster_time.m_as('ms')  # mT/m*ms
    qtm_pad = np.pad(qtm, (np.shape(qtm)[0] * pad_factor, np.shape(qtm)[0] * pad_factor))
    qstm = np.fft.fft(qtm_pad) * seq._system_specs.grad_raster_time.m_as('ms')  # mT/m*ms^2

    # P
    qtp = np.cumsum(gp[start_ind:end_ind]) * seq._system_specs.grad_raster_time.m_as('ms')  # mT/m*ms
    qtp_pad = np.pad(qtp, (np.shape(qtp)[0] * pad_factor, np.shape(qtp)[0] * pad_factor))
    qstp = np.fft.fft(qtp_pad) * seq._system_specs.grad_raster_time.m_as('ms')  # mT/m*ms^2

    # S
    qts = np.cumsum(gs[start_ind:end_ind]) * seq._system_specs.grad_raster_time.m_as('ms')  # mT/m*ms
    qts_pad = np.pad(qts, (np.shape(qts)[0] * pad_factor, np.shape(qts)[0] * pad_factor))
    qsts = np.fft.fft(qts_pad) * seq._system_specs.grad_raster_time.m_as('ms')  # mT/m*ms^2

    # Linearly combine MPS basis for each direction, the calculate final spectra
    S_list = []
    for dir in directions:
        dir = dir / np.linalg.norm(dir)
        S = Quantity(np.abs(qstm * dir[0] + qstp * dir[1] + qsts * dir[2]) ** 2, 'mT^2/m^2*ms^4')
        S_list.append(S)

    freq = np.arange(0, np.shape(qsts)[0]) / seq._system_specs.grad_raster_time.m_as('s') / np.shape(qsts)[0]

    return S_list, Quantity(freq, 'Hz')
