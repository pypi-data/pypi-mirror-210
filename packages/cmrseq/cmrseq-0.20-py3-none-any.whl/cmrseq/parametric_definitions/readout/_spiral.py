""" Private submodule containing spiral trajectory generation code"""
__all__ = ["spiral_pipezwart"]


from copy import deepcopy
import typing

from pint import Quantity
import numpy as np

import cmrseq


# pylint: disable=W1401, R0913, R0914, C0103
def spiral_pipezwart(system_specs: cmrseq.SystemSpec,
                     interleaves: int,
                     kr_max: Quantity,
                     kr_delta: Quantity,
                     spiral_type: str = "archimedean",
                     gradient_rewind_type: str = "ramp down",
                     undersampling_type: str = "none",
                     undersampling_start: float = 1.,
                     undersampling_end: float = 1.,
                     undersampling_factor: float = 1.,
                     kz_max: Quantity = Quantity(1., "1/m"),
                     kz_delta: Quantity = Quantity(1., "1/m")) -> cmrseq.Sequence:
    """ Generates spiral trajectory. Ported from C code provided along with:
    Pipe JG, Zwart NR. Spiral trajectory design: A flexible numerical algorithm and base
    analytical equations. Magn. Reson. Med. 2014;71:278–285 doi: 10.1002/mrm.24675.

    Original C code can be found at https://www.ismrm.org/mri_unbound/sequence.htm

    Some small changes to indexing when defining rewinder gradients and to address
     slew rate violations

    :param system_specs: SystemSpecifications
    :param interleaves: number of interleaved spirals
    :param kr_max: :math:`FOV_{kr, max}` corresponding to minimal radial
                    resolution :math:`1/\Delta r`
    :param kr_delta: k-space radial step-length
    :param spiral_type: str from ['Archimedean', 'spherical dst'] denoting the type of spiral
    :param gradient_rewind_type: str from [none, ramp down, rewind to center] denoting the type
                                    of gradient rewind
    :param undersampling_type: str from ['linear', 'quadratic', 'hanning'] defining the type of
                                undersampling during acquisition
    :param undersampling_start:
    :param undersampling_end:
    :param undersampling_factor:
    :param kz_max:
    :param kz_delta:
    :return:
    """
    ## internal parameters
    raster_subdivision = 4

    max_array = int(100 / system_specs.grad_raster_time.m_as("ms"))  # Assuming maximum 100ms spiral

    internal_raster = system_specs.grad_raster_time / raster_subdivision

    nyquist = interleaves * kr_delta

    gamrast = internal_raster * system_specs.gamma
    dgc = internal_raster * system_specs.max_slew  # max gradient change per internal raster

    sub_gamrast = gamrast * raster_subdivision
    sub_dgc = dgc * raster_subdivision

    # initialize arrays
    gsign = np.ones(raster_subdivision * max_array)
    kx = Quantity(np.zeros(raster_subdivision * max_array), "1/m")
    ky = Quantity(np.zeros(raster_subdivision * max_array), "1/m")
    kz = Quantity(np.zeros(raster_subdivision * max_array), "1/m")
    gxarray = Quantity(np.zeros(max_array), "mT/m")
    gyarray = Quantity(np.zeros(max_array), "mT/m")
    gzarray = Quantity(np.zeros(max_array), "mT/m")

    # start out spiral going radially at max slew-rate for 2 time-points
    kr_lim = kr_max - kr_delta / 2

    kx[1] = gamrast * dgc
    kx[2] = 3 * gamrast * dgc

    if spiral_type.lower() == "spherical dst":
        kz[0] = kz_max
        kz[1] = np.sqrt(kz_max ** 2 * (1 - ((kx[1] ** 2 + ky[1] ** 2) / kr_max ** 2)))
        kz[2] = np.sqrt(kz_max ** 2 * (1 - ((kx[2] ** 2 + ky[2] ** 2) / kr_max ** 2)))

    i = 2
    kr = kx[2]

    # Main loop

    while (kr <= kr_lim) and (i < (raster_subdivision * max_array - 1)):

        # determine k position at i+0.5 given constant velocity
        kmx = 1.5 * kx[i] - 0.5 * kx[i - 1]  # kx[i] + 0.5*(kx[i] - kx[i-1])
        kmy = 1.5 * ky[i] - 0.5 * ky[i - 1]
        kmr = np.sqrt(kmx ** 2 + kmy ** 2)

        # Calculate radial spacing

        rnorm = kmr / kr_max  # normalized k-space radius on [0,1]

        if rnorm <= undersampling_start:
            rad_spacing = 1
        elif rnorm < undersampling_end:
            us_i = (rnorm - undersampling_start) / (undersampling_end - undersampling_start)
            if undersampling_type.lower() == "linear":
                # Linear
                rad_spacing = 1 + (undersampling_factor - 1) * us_i
            elif undersampling_type.lower() == "quadratic":
                # Quadratic
                rad_spacing = 1 + (undersampling_factor - 1) * us_i ** 2
            elif undersampling_type.lower() == "hanning":
                # Hanning
                rad_spacing = 1 + (undersampling_factor - 1) * 0.5 * (1 - np.cos(us_i * np.pi))
            else:
                rad_spacing = 1
        else:
            rad_spacing = undersampling_factor

        # Undersample spiral for Spherical-Distributed Spiral
        if spiral_type.lower() == "spherical dst":
            if rnorm < 1.:
                rad_spacing = min(kz_max / kz_delta, rad_spacing / np.sqrt(1.0 - rnorm ** 2))
            else:
                rad_spacing = kz_max / kz_delta
        # Fermat spiral for floret
        if spiral_type.lower() == "fermat:floret" and rnorm > 0:
            rad_spacing *= 1. / rnorm

        # Set up spiral

        alpha = np.arctan(2 * np.pi * kmr / (rad_spacing * nyquist))
        phi = np.arctan2(kmy, kmx)
        theta = phi + alpha

        ux = np.cos(theta)
        uy = np.sin(theta)
        uz = 0
        gz = 0

        # Spherical DST
        if spiral_type.lower() == "spherical dst":
            kmz = 1.5 * kz[i] - 0.5 * kz[i - 1]
            uz = -((ux * kmx + uy * kmy) / kr_max ** 2) * (kz_max ** 2 / kmz)
            umag = np.sqrt(ux ** 2 + uy ** 2 + uz ** 2)
            ux = ux / umag
            uy = uy / umag
            uz = uz / umag
            gz = (kz[i] - kz[i - 1]) / gamrast

        # Find largest gradient amplitude for max slew

        gx = (kx[i] - kx[i - 1]) / gamrast
        gy = (ky[i] - ky[i - 1]) / gamrast

        term = dgc ** 2 - (gx ** 2 + gy ** 2 + gz ** 2) + (ux * gx + uy * gy + uz * gz) ** 2

        if term >= 0:
            gm = min((ux * gx + uy * gy + uz * gz) + gsign[i] * np.sqrt(term),
                     system_specs.max_grad)
            gx = gm * ux
            gy = gm * uy

            kx[i + 1] = kx[i] + gx * gamrast
            ky[i + 1] = ky[i] + gy * gamrast

            if spiral_type.lower() == "spherical dst":
                kz[i + 1] = np.sqrt(kz_max ** 2
                                    * (1 - ((kx[i + 1] ** 2 + ky[i + 1] ** 2) / kr_max ** 2)))

            i += 1
        else:
            while i > 3 and gsign[i - 1] == -1:
                i -= 1
            gsign[i - 1] = -1
            i = i - 2

        kr = np.sqrt(kx[i] ** 2 + ky[i] ** 2)
    # End of main loop

    # Now work on rewinders

    i_end = i

    gxsum = 0
    gysum = 0
    gzsum = 0
    j = 0
    for j in range(1, int(np.floor(i_end / raster_subdivision))):
        i1 = j * raster_subdivision
        i0 = (j - 1) * raster_subdivision
        gxarray[j] = (kx[i1] - kx[i0]) / sub_gamrast
        gyarray[j] = (ky[i1] - ky[i0]) / sub_gamrast
        gzarray[j] = (kz[i1] - kz[i0]) / sub_gamrast
        gxsum += gxarray[j]
        gysum += gyarray[j]
        gzsum += gzarray[j]

    gm = np.sqrt(gxarray[j] ** 2 + gyarray[j] ** 2 + gzarray[j] ** 2)
    ux = gxarray[j] / gm
    uy = gyarray[j] / gm
    uz = gzarray[j] / gm

    # Ramp to zero gradient
    if gradient_rewind_type is not None and (gradient_rewind_type.lower() == "ramp down"
                                             or gradient_rewind_type.lower() == "rewind to center"):
        gz_sum_ramp = 0

        j += 1

        while gm > 0 and j < max_array - 1:
            gm = max(Quantity(0., "mT/m"), gm - sub_dgc)
            gxarray[j] = gm * ux
            gyarray[j] = gm * uy
            gzarray[j] = gm * uz
            gxsum += gxarray[j]
            gysum += gyarray[j]
            gzsum += gzarray[j]
            gz_sum_ramp += gzarray[j]
            j += 1
    rampdown_end = j

    # Return to k=0
    if gradient_rewind_type is not None and gradient_rewind_type.lower() == "rewind to center":
        # Get direction for rewinder
        gsum = np.sqrt(gxsum ** 2 + gysum ** 2 + gzsum ** 2)
        # Only rewind x and y for spherical DST
        if spiral_type.lower() == "spherical dst":
            gsum = np.sqrt(gxsum ** 2 + gysum ** 2 + gz_sum_ramp ** 2)
        gsum0 = gsum
        ux = -gxsum / gsum
        uy = -gysum / gsum
        uz = -gzsum / gsum
        if spiral_type.lower() == "spherical dst":
            uz = -gz_sum_ramp / gsum
        gsum_ramp = 0.5 * gm * (gm / sub_dgc)

        # Ramp up strength and hold until ramp down will take us just past the center
        while gsum_ramp < gsum and j < (max_array - 1):
            gm = min(system_specs.max_grad, gm + sub_dgc)
            gxarray[j] = gm * ux
            gyarray[j] = gm * uy
            gzarray[j] = gm * uz
            gsum -= gm
            j += 1
            gsum_ramp = 0.5 * gm * (gm / sub_dgc)

        # extra point to prevent slew rate issues
        gm = min(system_specs.max_grad, gm + sub_dgc)
        gxarray[j] = gm * ux
        gyarray[j] = gm * uy
        gzarray[j] = gm * uz
        gsum -= gm
        j += 1

        # ramp down (with some overshoot for now)
        while gm > 0 and j < max_array - 1:
            gm = max(Quantity(0., "mT/m"), gm - sub_dgc)
            gxarray[j] = gm * ux
            gyarray[j] = gm * uy
            gzarray[j] = gm * uz
            gsum -= gm
            j += 1
        rewind_end = j

        # Correct rewinder to take us exactly to k=0
        gradtweak = gsum0 / (gsum0 - gsum)

        if gradtweak > 1:
            raise ValueError("Something went wrong in rewinder calculation, slew rate exceeded")

        for j in range(rampdown_end, rewind_end):
            gxarray[j] *= gradtweak
            gyarray[j] *= gradtweak
            gzarray[j] *= gradtweak

    # end of gradient adjustments

    # Create a gradient objects

    time = system_specs.grad_raster_time * np.arange(0, j + 1)
    wf = np.transpose(
        np.concatenate((gxarray[0:(j + 1), np.newaxis],
                        gyarray[0:(j + 1), np.newaxis],
                        gzarray[0:(j + 1), np.newaxis]), axis=1))
    gradient = cmrseq.bausteine.ArbitraryGradient(system_specs=system_specs,
                                                  time_points=time, waveform=wf,
                                                  name="spiral_readout")
    return cmrseq.Sequence([gradient], system_specs=system_specs)
