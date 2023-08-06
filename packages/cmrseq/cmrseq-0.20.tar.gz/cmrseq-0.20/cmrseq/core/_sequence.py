""" This Module contains the implementation of the core functionality Sequence"""
__all__ = ["Sequence"]

from copy import deepcopy
from typing import List, Union, Iterable, Tuple, Dict
from warnings import warn
import re

import numpy as np
from pint import Quantity
from tqdm import tqdm

from cmrseq.core.bausteine._base import SequenceBaseBlock
from cmrseq.core.bausteine._adc import ADC
from cmrseq.core.bausteine._rf import RFPulse
from cmrseq.core.bausteine._gradients import Gradient
from cmrseq.core._system import SystemSpec


class Sequence:
    """ This class serves as a container for MRI-sequence building blocks.

    All blocks contained in a sequence are kept as mutable objects of type SequenceBaseBlock or
    rather its subclasses. This means if a contained block is changed/transformed outside
    the sequence scope, these changes are also reflected in the sequence.

    Below, the functionality provided by a cmrseq.Sequence object is explained according to the
    groups:

    - Instantiation and composition
    - Get contained blocks
    - Gridding, Moments and K-space


    **Instantiation and composition**

    To instantiate a Sequence you need a list containing building blocks and a sytem-specification
    definition. On instantiation, all blocks are validated against the system limits. If any block
    violates the limits, an exception is raised.

    _Adding blocks_: Blocks or even entire sequences can be added to an existing sequence object
    one the obe hand by using the 'add_block', 'append', 'extend' methods (see documentation).
    And on the other hand, the Sequence class implements the addition operator, which combines
    two sequence objects into either a new object containing copies of all blocks contained in the
    other two or by in-place addition where no copies are made:

    .. code::

        new_sequence_object = sequence1 + sequence2   # Combination with copy
        sequence1 += sequence2                        # inplace combination of seq2 into seq1


    _Unique names_: a sequence objects keeps a mapping of automatically created unique names to the
    actual blocks. Whenever blocks are added

    **Get contained blocks**

    There are multiple ways to query single or even multiple blocks at once from the sequence
    object. To get a complete list of unique block-names use the property `seq.blocks`.

    __Access by name__:
    1. Indexing by unique name: `seq["trapezoidal_0"]`
    2. Get all blocks by partial string match: `seq.get_block(partial_string_match=...)`
    3. Get all blocks by matching regular expression on unique names: `seq.get_block(regular_expression=...)`

    __Assuming temporal order of start__
    1. Indexing by integer: `seq[0]`
    2. Indexing by slice: `seq[0:5]`
    3. Indexing by tuple of integers: `seq[(0, 2, 5)]`
    4. Iterating over sequence: `[block for block in seq]`
    5. Iterating over sequence with block-names `{name: block for (name, block) in seq.items()}`


    **Gridding, Moments and K-space**

    Gradients, RF and ADCs represented on a dense temporal grid defined by the system raster times
    can be obtained by calling the methods: `gradients_to_grid`, `rf_to_grid`, and `adc_to_grid`.

    Gradient moments of specified order can be integrated using the function `calculate_moment`.

    To get a representation of the kspace-trajectory as well as timing and position of sampling
    events defined by contained ADC blocks can be obtained by the `calculate_kspace` function.


    :param building_blocks: List of building Blocks
    :param system_specs: Instance of SystemSpec
    """

    #: System specification object
    _system_specs: SystemSpec
    #:
    _blocks: List[SequenceBaseBlock]
    #:
    _block_lookup: Dict[str, SequenceBaseBlock]

    def __init__(self, building_blocks: List[SequenceBaseBlock], system_specs: SystemSpec):
        self._system_specs = system_specs
        self._blocks = building_blocks
        self.validate()

        self._block_lookup = {}
        for block in self._blocks:
            self._add_unique_block_name(block)


    def __add__(self, other: 'Sequence') -> 'Sequence':
        """ If both system specifications match, returns a new sequence containing deep copies
        of all blocks contained in self._blocks and other._blocks """
        self._check_sys_compatibility(other._system_specs)
        new_blocks = [deepcopy(b) for b in [*self._blocks, *other._blocks]]
        return Sequence(new_blocks, system_specs=deepcopy(self._system_specs))

    def __iadd__(self, other: "Sequence"):
        """ """
        self._check_sys_compatibility(other._system_specs)
        for b in other._blocks:
            self._add_unique_block_name(b)
            self._blocks.append(b)
        return self

    def __getitem__(self, item: Union[str, int, slice, tuple]):
        """ Possible ways to index/query blocks in a sequence:

        .. code::

            seq[0], seq[0:4], seq[(0, 4, 1)] -> returns block by index assuming ordering
                        according to start time

            seq["trapezoidal_0"] -> returns block by name



        :param item:
        :return:
        """
        if isinstance(item, str):
            return self._block_lookup[item]
        elif isinstance(item, int):
            names_and_times = self._create_sorted_block_list(reversed=False)
            return self._block_lookup[names_and_times[item][0]]
        elif isinstance(item, slice):
            names_and_times = self._create_sorted_block_list(reversed=False)
            return [self._block_lookup[k] for k, _ in names_and_times[item]]
        elif isinstance(item, tuple):
            if not all([isinstance(i, int) for i in item]):
                raise NotImplementedError("When indexing with a tuple, all tuple entries must"
                                          f" be of type int. But got {item}!")
            names_and_times = self._create_sorted_block_list(reversed=False)
            return [self._block_lookup[names_and_times[i][0]] for i in item]
        else:
            raise NotImplementedError(f"{type(item)} is not in the list of possible block"
                                      f" queries [str, int, slice, Tuple[int]]")

    def __iter__(self):
        """Returns an iterator yielding blocks sorted by theirs start time"""
        start_times = self._create_sorted_block_list(reversed=False)
        return (self._block_lookup[k] for (k, _) in start_times)

    def items(self):
        """Returns a generator yielding (unique_block_name, block) tuples"""
        names_and_times = self._create_sorted_block_list(reversed=False)
        return ((k, self._block_lookup[k]) for (k, _) in names_and_times)

    def _add_unique_block_name(self, block: SequenceBaseBlock):
        """Iterates over block names and adds a counter to the block name if it already is used to
        create the dictionary (unique_block_name -> SequenceBaseBlock)
        :param block:
        """
        i = 0
        augmented_name = block.name + f"_{i}"
        while self._block_lookup.get(augmented_name, None) is not None:
            augmented_name = block.name + f"_{i}"
            i += 1
        self._block_lookup.update({augmented_name: block})

    def _check_sys_compatibility(self, system_specs: SystemSpec):
        equalities = [self._system_specs.__dict__[k] == system_specs.__dict__[k]
                      for k in self._system_specs.__dict__.keys()]
        if not all(equalities):
            raise ValueError("System specifications of added sequence do not match. Addition "
                             "for different system specifications is not implemented")

    def _create_sorted_block_list(self, reversed: bool = False):
        start_times = [(k, b.tmin) for k, b in self._block_lookup.items()]
        start_times.sort(key=lambda x: float(x[1].m_as("ms")), reverse=reversed)
        return start_times

    def validate(self) -> None:
        """ Calls the validation function of each block with self._system_specs

        :raises ValueError: If any contained block fails to validate with own system specs
        """
        for block in self._blocks:
            block.validate(system_specs=self._system_specs)

    def add_block(self, block: SequenceBaseBlock, copy: bool = True) -> None:
        """ Add the instance of block to the internal List of sequence blocks.

        **Note**: The internal definiton of blocks is mutuable, therefore if the new block is not
        copied, subsequent alterations can have unwanted side-effects inside the sequence.

        :raises ValueError: If block.validate() fails to validate using the system specs of self
        :raises TypeError: If block is an instance of class SequenceBaseBlock

        :param block: Sequence block to be added to the sequence
        :param copy: Determines if the block is copied before adding it to the sequence
        """

        if not isinstance(block, SequenceBaseBlock):
            raise NotImplementedError("Method only defined for instances of SequenceBaseBlocks."
                                      f"Got {type(block)}")
        try:
            block.validate(self._system_specs)
        except ValueError as err:
            raise ValueError("New block does not validate against sequence system specifications."
                             f"Resulting in following ValueError: {err}") from err
        if copy:
            block = deepcopy(block)
        self._blocks.append(block)
        self._add_unique_block_name(block)

    def rename_blocks(self, old_names: List[str], new_names: List[str]):
        """ Renames blocks and updates block lookup map"""
        for old, new in zip(old_names, new_names):
            bl = self._block_lookup[old]
            bl.name = new
        self._block_lookup = {}
        for block in self._blocks:
            self._add_unique_block_name(block)

    def remove_block(self, block_name: str):
        """ Removes block from internal lookup """
        block = self.get_block(block_name)
        if block is None:
            raise ValueError(f"Tried to remove non-existing block; \n "
                             f"'{block_name}' not in {self.blocks}")
        block_index = [block is b for b in self._blocks].index(True)
        del self._blocks[block_index]
        del self._block_lookup[block_name]


    def append(self, other: Union['Sequence', SequenceBaseBlock],
               copy: bool = True, end_time: Quantity = None) -> None:
        """If both system specifications match, copies all blocks from `other` shifts them by own
        tmax and adds the blocks to own collection

        :raises ValueError: If other fails to validate using the system specs of self

        :param other: Sequence or block to be added to the sequence
        :param copy: if true copies the other sequence object
        :param validate: if True
        :param end_time:
        """
        if isinstance(other, SequenceBaseBlock):
            try:
                other.validate(self._system_specs)
            except ValueError as err:
                raise ValueError(
                    "New block does not validate against sequence system specifications."
                    f"Resulting in following ValueError: {err}") from err
            block_copies = [other, ]
        elif isinstance(other, Sequence):
            self._check_sys_compatibility(other._system_specs)  # pylint: disable=W0212
            block_copies = [other.get_block(block_name) for block_name in other.blocks]
        else:
            raise NotImplementedError(f"Cannot append object of type {type(other)} to Sequence")

        if copy:
            block_copies = [deepcopy(block) for block in block_copies]

        if end_time is None:
            if not self._blocks:
                end_time = Quantity(0., "ms")
            else:
                end_time = np.max([block.tmax.m_as("ms") for block in self._blocks])

        for block in block_copies:
            block.shift(Quantity(end_time, "ms"))
        self._blocks.extend(block_copies)
        for block in block_copies:
            self._add_unique_block_name(block)

    def extend(self, other: Iterable[Union['Sequence', SequenceBaseBlock]],
               copy: bool = True) -> None:
        """If both system specifications match, copies all blocks from `other` shifts them by own
        tmax and adds the blocks to own collection

        :raises ValueError: If other fails to validate using the system specs of self

        :param other: ListSequence or block to be added to the sequence
        :param copy: if true copies the other sequence object
        """

        end_times = [b.end_time.m_as("ms") if isinstance(b, Sequence) else b.tmax.m_as("ms")
                     for b in other]
        end_times = np.cumsum([self.end_time.m_as("ms")] + end_times)
        for idx, other_it in enumerate(tqdm(other, desc="Extending Sequence")):
            self.append(other_it, copy, end_time=end_times[idx])

    def get_block(self, block_name: Union[str, Iterable[str]] = None,
                  partial_string_match: Union[str, Iterable[str]] = None,
                  regular_expression: Union[str, Iterable[str]] = None) \
            -> Union[SequenceBaseBlock, List[SequenceBaseBlock]]:
        """ Returns reference to the block whose member `name` matches the specified argument.
        If no block with given name is present in the sequence, it returns None

        .. note::

            Checks which keyword argument to use from left to right as specified in the signature.
            If multiple are specified uses only the first one.

        :raises: ValueError if no keyword-argument is specified

        :param block_name: String or iterable of strings exactly matching a set of blocks contained
                            in the sequence
        :param partial_string_match: str or iterable of strings that specify partial string matches.
                            All blocks partially matching at least one are returned.
        :param regular_expression: str or iterable of strings containing regular expressions that
                            are matched against the block-names. All blocks, matching at least one
                            of the given expressions are returned.
        :return: SequenceBaseBlock or List of SequenceBaseBlocks depending on the specified argument
        """
        if block_name is not None:
            if isinstance(block_name, str):
                return self._block_lookup.get(block_name, None)
            else:
                return [self._block_lookup[bn] for bn in block_name]
        elif partial_string_match is not None:
            if isinstance(partial_string_match, str):
                partial_string_match = [partial_string_match, ]
            partial_string_match = "|".join([f"(?:.*{p}.*)" for p in partial_string_match])
            matched_block_names = [block for name, block in self._block_lookup.items()
                                   if re.match(partial_string_match, name)]
            return matched_block_names
        elif regular_expression is not None:
            if isinstance(regular_expression, str):
                regular_expression = [regular_expression, ]
            regular_expression = "|".join([f"(?:{p})" for p in regular_expression])
            matched_block_names = [block for name, block in self._block_lookup.items()
                                   if re.match(regular_expression, name)]
            return matched_block_names
        else:
            raise ValueError("At least one on the keyword arguments must be specified")

    def shift_in_time(self, shift: Quantity) -> None:
        """ Shifts all blocks contained in the sequence object by the specified time

        :param shift: Quantity of dimesion time
        """
        for block in self._blocks:
            block.shift(time_shift=shift)

    def time_reverse(self) -> None:
        """ Reverses the sequence in time
        """
        # flip about end of sequence
        time_flip_point = self.duration
        for block in self._blocks:
            block.flip(time_flip_point)

    def invert_gradients(self) -> None:
        """Inverts all gradient amplitudes in sequence
        """
        for block in self._blocks:
            block.scale_gradients(-1.)

    def rotate_gradients(self, rotation_matrix: np.ndarray) -> None:
        """Rotates all gradients according to specified rotation matrix

        :param rotation_matrix: (3, 3) rotation matrix containing the new column basis vectors
            (meaning in [:, i], i indexes the new orientation of MPS).
            Vectors are normalized along axis=0 to ensure same magnitude
        """
        for block in self._blocks:
            if block.gradients is not None:
                block.rotate_gradients(rotation_matrix)

    @property
    def duration(self) -> Quantity:
        """Time difference of earliest start and latest end of all blocks contained in the sequence
        """
        return self.end_time - self.start_time

    @property
    def start_time(self):
        return Quantity(np.round(np.min([b.tmin.m_as("ms") for b in self._blocks]), 6), 'ms')

    @property
    def end_time(self):
        return Quantity(np.round(np.max([b.tmax.m_as("ms") for b in self._blocks]), 6), 'ms')

    @property
    def gradients(self) -> List[Tuple[Quantity, Quantity]]:
        """ Returns the gradient definitions (t, wf) of all blocks that are contained in the
        sequence. Blocks that do not contain a gradient definition are ignored"""
        return [block.gradients for block in self._blocks if isinstance(block, Gradient)]

    @property
    # pylint: disable=C0103
    def rf(self) -> List[Tuple[Quantity, Quantity]]:
        """ Returns the rf definitions (t, amplitude) of all blocks that are contained in the
                sequence. Blocks that do not contain a rf definition are ignored"""
        return [block.rf for block in self._blocks if isinstance(block, RFPulse)]

    @property
    def rf_events(self) -> List[Tuple[Quantity, Quantity]]:
        """ Returns the rf definitions (t, amplitude) of all blocks that are contained in the
                sequence. Blocks that do not contain a rf definition are ignored"""
        return [block.rf_events for block in self._blocks if isinstance(block, RFPulse)]

    @property
    def adc_centers(self) -> List[Quantity]:
        """ Returns the centers of all adc_blocks in the sequence."""
        return [block.adc_center for block in self._blocks if isinstance(block, ADC)]

    @property
    def blocks(self) -> Tuple[str]:
        """Returns a tuple containing the names of all blocks contained in the sequence object,
        where temporal ordering is assumed"""
        names_and_times = self._create_sorted_block_list(reversed=False)
        names = [n for n, t in names_and_times]
        return names

    # pylint: disable=R0914, C0103
    def gradients_to_grid(self) -> Tuple[np.ndarray, np.ndarray]:
        """ Grids gradient definitions of all blocks contained in the sequence, on a joint time grid
        from the minimal to maximal value in single time-points definitions with a step-length
        defined in system_specs.grad_raster_time.
        If gradients occur at the same time on the same channel, they are added.

        :return: (np.ndarray, np.ndarray) of shape (t, ) containing the time-grid and
            (3 [gx, gy, gz], t) containing the waveform definition definition in ms and mT/m
        """

        gradients = self.gradients
        if not gradients:
            return None, None

        time_points = [g[0].m_as("ms") for g in gradients]
        wave_forms = [g[1].m_as("mT/m") for g in gradients]

        dt = self._system_specs.grad_raster_time.m_as("ms")
        t_grid = np.arange(0, self.end_time.m_as("ms") + dt, dt)
        wf_grid = np.zeros((3, t_grid.shape[0]))

        for t, wf, bidx in zip(time_points, wave_forms, range(len(self._blocks))):
            t = np.array(t)
            tidx = np.around(t / dt)
            if not np.allclose(t / dt, tidx, rtol=1e-6):
                warn(f"Gradient definition of block {bidx} is not on gradient raster")
            start, end = int(tidx[0]), int(tidx[-1])
            interpolated_wfx = np.interp(t_grid[start:end], t, wf[0])
            interpolated_wfy = np.interp(t_grid[start:end], t, wf[1])
            interpolated_wfz = np.interp(t_grid[start:end], t, wf[2])
            wf_grid[:, start:end] += np.stack([interpolated_wfx,
                                               interpolated_wfy,
                                               interpolated_wfz])
        return t_grid, wf_grid

    # pylint: disable=R0914, C0103
    def rf_to_grid(self) -> Tuple[np.ndarray, np.ndarray]:
        """ Grids RF-definitions of all blocks contained in the sequence, on a joint time grid
        from the minimal to maximal value in single time-points definitions with a step-length
        defined in system_specs.rf_raster_time.

        If gradients occur at the same time on the same channel, they are added.

        :return: (np.ndarray, np.ndarray) of shape (1, t) containing the time-grid and
                (1, t) containing the complex RF amplitude
        """
        rf = self.rf
        if not rf:
            return None, None

        time_points = [r[0].m_as("ms") for r in rf]
        wave_forms = [r[1].m_as("mT") for r in rf]

        dt = self._system_specs.rf_raster_time.m_as("ms")
        t_grid = np.arange(0, self.end_time.m_as("ms") + dt, dt)
        rf_grid = np.zeros((t_grid.shape[0]), dtype=np.complex64)

        for t, complex_alpha, bidx in zip(time_points, wave_forms, range(len(rf))):
            t = np.array(t)
            tidx = np.around(t / dt)
            if not np.allclose(t / dt, tidx, rtol=1e-6):
                warn(f"RF definition of block {bidx} is not on RF raster")
            start, end = int(tidx[0]), int(tidx[-1])
            rf_grid[start:end] += np.interp(t_grid[start:end], t, complex_alpha)
        return t_grid, rf_grid

    # pylint: disable=R0914, C0103
    def adc_to_grid(self, force_raster: bool = False) \
            -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Grids the ADC-Events of all blocks contained in the sequence as boolean 1D mask along
        with the resulting time-grid. Additionally the start and end points of the all adc-blocks
        are returned. The definition of start/end differ for force_gradient_raster True/False

        **Boolean mask explanation**:

            - *force_raster* == `False`
                                events that are not defined on the grid, are inserted into the
                                time-raster resulting in a non-uniform time definition.
                                The boolean values of the newly inserted points are set to 1.
            - *force_raster* == `True`
                                for events that are not defined on the grid the boolean values
                                of the interval borders on gradient raster time are set to 1.
                                For events that are already on the grid, the corresponding single
                                index is set 1.

        **Start/End - definition**:

            - *force_raster* == `False`:
                the exact time of first/last event per block is returned.
            - *force_raster* == `True`:
                The returned start/end times correspond to the beginning and end of the plateau
                of a trapezoidal gradient played out during the adc-events (addition of dwell-time).

        :param force_raster: bool - defaults to True
        :return: Tuple(np.array, np.array, np.array)
                      - (t, ) containing time-values
                      - (t, ) containing values of 0 or 1, indicating where the adc is active
                      - (t, ) containing the adc_phase in radians
                      - (#adc_blocks, 2) where (:, 0) contains the indices of the start time of the adc-block and (:, 1) the end time correspondingly.
        """
        # First grid all individual blocks on adc_raster times
        adc_blocks = [block for block in self._blocks if isinstance(block, ADC)]
        gridded_adcs = []
        for block in adc_blocks:
            gridded_adcs.append(self._grid_single_adc_block(force_raster, block))

        # Secondly Insert the gridded adc-timings into the gradient raster
        gradient_raster = self.gradients_to_grid()[0]

        # Make sure that all gridded adc times are within the boundaries of gradient_raster because
        # Otherwise the insertion logic below will fail
        latest_adc_raster_time = np.max([np.max(t[0]) for t in gridded_adcs])
        first_adc_raster_time = np.min([np.min(t[0]) for t in gridded_adcs])
        if gradient_raster is None:
            gradient_raster = np.arange(first_adc_raster_time, latest_adc_raster_time,
                                        self._system_specs.grad_raster_time.m_as("ms"))
        if gradient_raster[-1] <= latest_adc_raster_time:
            gradient_raster = np.append(gradient_raster, latest_adc_raster_time)

        # Concatenate gridded adcs, sort the adcs according to their initial value of t
        gridded_adcs.sort(key=lambda v: v[0][0])
        adc_raster_time = np.around(np.concatenate([v[0] for v in gridded_adcs]), decimals=6)
        adc_on = np.concatenate([v[1] for v in gridded_adcs])
        adc_phase = np.concatenate([v[2] for v in gridded_adcs])
        if not np.all(np.diff(adc_raster_time) >= 0):
            raise ValueError("Currently gridding sequences with ADCs is only possible for "
                             "non-overlapping ADC-blocks")

        # Find positions to insert
        gradient_raster = np.around(gradient_raster, decimals=6)
        insertion_idx = np.searchsorted(gradient_raster, adc_raster_time, side="left")

        # Insert points into time raster and allocate the adc_on/phase arrays
        # while ignore points that are already on the gradient raster
        gradient_raster = np.insert(gradient_raster, insertion_idx, adc_raster_time)
        gradient_raster = np.unique(np.around(gradient_raster, decimals=6))
        adc_activation_raster = np.zeros_like(gradient_raster)
        adc_phase_raster = np.zeros_like(gradient_raster)

        # Recalculate indices to set values for phase and activation and set values accordingly
        setting_idx = np.searchsorted(gradient_raster, adc_raster_time, side="left")
        adc_activation_raster[setting_idx] = adc_on
        adc_phase_raster[np.where(adc_activation_raster)] = adc_phase
        start_end_per_event = []
        for time_raster, _, _ in gridded_adcs:
            s_e = np.searchsorted(gradient_raster, np.stack([time_raster[0], time_raster[-1]]))
            start_end_per_event.append(s_e)
        start_end_per_event = np.stack(start_end_per_event)

        return gradient_raster, adc_activation_raster, adc_phase_raster, start_end_per_event

    def _grid_single_adc_block(self, force_raster: bool, block: ADC) \
            -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """ Grids a single adc-block to raster

        :param force_raster: bool
        :param block: Block that is a subclass of cmrseq.bausteine.ADC
        :return: (time_raster, adc_activation_raster, adc_phase_raster)
        """

        rounded_adc_timings = np.around(block.adc_timing.m_as("ms"), decimals=6)
        dt = np.round(self._system_specs.adc_raster_time.m_as("ms"), decimals=6)
        time_raster = np.around(np.arange(block.tmin.m_as("ms"), block.tmax.m_as("ms") + dt, dt),
                                decimals=6)
        phase = block.adc_phase

        sampling_idx = np.searchsorted(time_raster, rounded_adc_timings, side="left")
        idx_not_on_raster = np.logical_not(np.isclose(time_raster[sampling_idx],
                                                      rounded_adc_timings, atol=1e-6))
        sampling_idx_left_shift = sampling_idx[idx_not_on_raster] - 1

        if force_raster:
            augmented_idx = np.sort(np.concatenate([np.squeeze(sampling_idx),
                                                    sampling_idx_left_shift]))
            unique_sampling_indice = np.unique(augmented_idx, return_counts=False,
                                               return_index=False, return_inverse=False)
            adc_on = np.zeros_like(time_raster)
            adc_on[unique_sampling_indice] = 1
            phase = np.insert(phase, np.where(idx_not_on_raster)[0] + 1, phase[idx_not_on_raster])
        else:
            time_raster = np.insert(time_raster, sampling_idx[idx_not_on_raster],
                                    rounded_adc_timings[idx_not_on_raster])
            adc_on = np.zeros_like(time_raster)
            adc_on[np.searchsorted(time_raster, rounded_adc_timings, side="left")] = 1

        return np.around(time_raster, decimals=6), adc_on, phase

    # pylint: disable=R0914, C0103
    def calculate_kspace(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """ Evaluates the k-space trajectory of the sequence.

        **Note**: All RF-pulses with a smaller flip-angle other than 180° are assumed to be
        excitation pulses. 180° - Refocusing pulses result in a complex conjugation of the
        trajectory. Consecutive excitation pulses are handled by starting from k-space center again.

        :return: Tuple of arrays containing:

                - k-space trajectory on gradient rasters (-1, 3) in 1/m
                - k-space points at adc events (-1, 3) in 1/m
                - time at adc events (-1 ) in ms
        """
        # Subdivide gradient waveforms in periods between rf events for integration
        rf_events = [block.rf_events for block in self._blocks if isinstance(block, RFPulse)]

        if rf_events:
            rf_factors = []
            for (t, fa) in rf_events:
                factor = -1. if np.isclose(fa, np.pi, rtol=np.pi / 50) else 0.
                rf_factors.append([t.m_as("ms"), factor])
            rf_factors = np.stack(rf_factors)
            rf_factors = rf_factors[np.argsort(rf_factors[:, 0])]
        else:
            rf_factors = None

        t_grid_global, gradient_waveform = self.gradients_to_grid()
        k_of_t = np.zeros([3, gradient_waveform.shape[1]])

        if rf_factors is not None:
            rf_event_tidx = np.searchsorted(t_grid_global, rf_factors[:, 0])
            rf_event_tidx = np.concatenate([rf_event_tidx, [-1, ]])
            for idx, factor in enumerate(rf_factors[:, 1]):
                start, end = rf_event_tidx[idx:idx + 2]
                dt = np.diff(t_grid_global[start:end]).reshape(1, -1)
                wf = gradient_waveform[:, start:end]
                delta_k = np.cumsum(dt * (wf[:, 1:] + wf[:, 0:-1]) / 2, axis=1)
                delta_k *= self._system_specs.gamma.m_as("MHz/T")  # 1/mT/ms
                k_of_t[:, start + 1:end] = factor * k_of_t[:, start - 1:start] + delta_k
        else:
            k_of_t[:, 1:] = np.cumsum(np.diff(t_grid_global).reshape(1, -1) *
                                      (gradient_waveform[:, 1:] + gradient_waveform[:, :-1]) / 2,
                                      axis=1) * self._system_specs.gamma.m_as("MHz/T")

        # Evaluate k-space position at adc-events
        all_adc_timings = [block.adc_timing.m_as("ms") for block in self._blocks
                           if isinstance(block, ADC)]
        if all_adc_timings:
            t_adc = np.around(np.concatenate(all_adc_timings, axis=0), decimals=6)
            k_adc = np.stack([np.interp(t_adc, t_grid_global, k) for k in k_of_t])
        else:
            k_adc = None
            t_adc = None

        return k_of_t, k_adc, t_adc

    # pylint: disable=R0914, C0103
    def calculate_moment(self, moment: int = 0, center_time: Quantity = Quantity(0., "ms"),
                         end_time: Quantity = None, start_time: Quantity = None):
        """ Calculates gradient moments about a given center point

        :param moment: int of desired moment number
        :param center_time: Quantity of center time to calculate moment about
        :param end_time: Time to calculate moment up to, default is end of sequence
        :param start_time: Time to calculate moment from, default is start of sequence
        :return: List of moments, [Mx, My, Mz]
        """
        gradients = [block.gradients for block in self._blocks if block.gradients is not None]
        if not gradients:
            return Quantity([0., 0., 0.], 'mT/m * ms**' + str(moment + 1))

        if end_time is None and start_time is None:

            time_points = [g[0].m_as("ms") for g in gradients]
            wave_forms = [g[1].m_as("mT/m") for g in gradients]
            ct = center_time.m_as("ms")
            N = moment
            M = np.zeros([3, ])

            # Compute directly from ungridded waveform points using analytic formula
            for t, wf in zip(time_points, wave_forms):
                t = np.array(t)

                G = wf[:, 0:-1]
                dG = wf[:, 1:] - G
                tau = t[0:-1] - ct
                taup = t[1:] - ct
                dt = taup - tau

                M = M + np.sum(G / (N + 1) * (taup ** (N + 1) - tau ** (N + 1))
                               + dG / (dt * (N + 1) * (N + 2)) *
                               (taup ** (N + 1) * ((N + 1) * dt - tau) + tau ** (N + 2)),
                               axis=1)

                moments = Quantity(M.tolist(), 'mT/m*ms**' + str(N + 1))

        else:

            time, wf = self.gradients_to_grid()
            if end_time is not None:
                end_ind = np.argmin(
                    abs(time - (self._system_specs.time_to_raster(end_time)).m_as("ms")))
            else:
                end_ind = -2

            if start_time is not None:
                start_ind = np.argmin(
                    abs(time - (self._system_specs.time_to_raster(start_time)).m_as("ms")))
            else:
                start_ind = 0

            wf = wf[:, start_ind:end_ind + 1]
            time = time[start_ind:end_ind + 1]

            t = time - center_time.m_as("ms")
            mx = sum(wf[0] * t ** moment * self._system_specs.grad_raster_time.m_as("ms"))
            my = sum(wf[1] * t ** moment * self._system_specs.grad_raster_time.m_as("ms"))
            mz = sum(wf[2] * t ** moment * self._system_specs.grad_raster_time.m_as("ms"))

            moments = Quantity([mx, my, mz], 'mT/m*ms**' + str(moment + 1))

        return moments
