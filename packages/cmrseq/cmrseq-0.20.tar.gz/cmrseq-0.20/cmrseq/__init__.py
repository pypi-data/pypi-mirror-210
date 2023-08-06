__version__ = '0.20'
""" cmrseq - A package for defining and modifying Magnetic Resonance Sequences """
__all__ = ["bausteine", "Sequence", "SystemSpec", "seqdefs", "plotting", "utils", "io","contrib"]

from cmrseq.core import bausteine
from cmrseq.core._sequence import Sequence
from cmrseq.core._system import SystemSpec
import cmrseq.parametric_definitions as seqdefs

import cmrseq.plotting
import cmrseq.utils
import cmrseq.io
import cmrseq.contrib
