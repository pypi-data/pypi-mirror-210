""" This module contains plotting functionality to illustrate sequence definitions in a commonly
occuring format.
"""
__all__ = ["plot_moment", "plot_sequence", "plot_kspace_2d", "plot_kspace_3d", "plot_block_names","plot_gradient_spectra"]

from typing import Tuple, List

import numpy as np
from pint import Quantity
import matplotlib.pyplot as plt
from matplotlib import lines
import matplotlib.patches as patches
from mpl_toolkits.mplot3d.axes3d import Axes
from matplotlib.ticker import FormatStrFormatter

from cmrseq.core._sequence import Sequence
from cmrseq.core.bausteine import ADC
import cmrseq


# pylint: disable=R0914, W0212, C0103, W0106
def plot_moment(seq: Sequence, moment_order: int = 0,
                axes: Tuple[plt.Axes] = None) -> plt.Figure:
    """ Creates a figure with a 3x1 subplot grid and plots the gradient moment
     of specified order for all 3 gradient components over time. Also plots gradients superimposed
     into the corresponding subplot

    :param seq: Instance of cmrseq.Sequence
    :param moment_order: order of the moment to be plotted
    :param fig: plt figure containing 3 axes
    :return: plt.figure with 3x1 suplot grid
    """
    time, gradient_waveform = seq.gradients_to_grid()
    moment_integrand =  gradient_waveform * (time ** moment_order)
    gradient_moment = np.cumsum(moment_integrand, axis=1)

    grad_range = np.array([-seq._system_specs.max_grad.m_as("mT/m"),
                           seq._system_specs.max_grad.m_as("mT/m")])

    if axes is None:
        fig, axes = plt.subplots(3, 1, sharex='col', figsize=(8, 8))

    twin = []
    # get short symbol of moment which is a pin feature:
    # https://stackoverflow.com/questions/65681490/format-pint-unit-as-short-form-symbol
    # moment_unit = format(Quantity(1, f"mT/m*ms**{moment_order}"), "~")
    moment_unit = f"mT/m*ms^{moment_order}"
    moment_strings = ["", "st", "nd"] + ["th"] * 100
    moment_label = f"{moment_order}" + "^{{" + moment_strings[moment_order] + "}}"
    for idx, ax, grad_channel, moment_channel, label_m, label_g in zip(
                                range(3), axes, gradient_waveform, gradient_moment,
                                ["Mx[$"+moment_unit+"$]", "My[$"+moment_unit+"$]",
                                 "Mz[$"+moment_unit+"$]"], ["Gx [mT/m]", "Gy [mT/m]", "Gz [mT/m]"]):
        ax.plot(time, grad_channel, color="gray")
        ax.set_ylim(grad_range * 1.1)
        ax.set_yticks(np.linspace(grad_range[0], grad_range[1], 5))
        ax.set_ylabel(label_g)
        ax.grid(True)
        ax.yaxis.set_major_formatter(FormatStrFormatter('%3.2f'))

        twinax = ax.twinx()
        twinax.tick_params("y", colors=f"C{idx}", direction="in")
        twinax.yaxis.set_label_position('left')
        twinax.yaxis.label.set_color(f"C{idx}")
        twinax.yaxis.set_ticks_position('left')
        twinax.plot(time, moment_channel, color=f"C{idx}")
        ylim = np.max((np.max(abs(moment_channel)), 1))
        twinax.set_ylim(-ylim * 1.1, ylim * 1.1)
        twinax.set_yticks(np.linspace(-ylim, ylim, 5))
        twinax.yaxis.set_major_formatter(FormatStrFormatter('%3.2f'))
        twinax.set_ylabel(label_m, labelpad=20)
        twinax.legend([lines.Line2D([0], [0], ls='-', c='gray'),
                       lines.Line2D([0], [0],  ls='--', c=f'C{idx}')],
                      ['Gradient', f"${moment_label}$ Moment"])
        twin.append(twinax)

    axes[-1].set_xlabel("Time [ms]")
    for ax, tax in zip(axes, twin):
        [tick.set_verticalalignment("bottom") for tick in ax.get_yticklabels()]
        [tick.set_verticalalignment("top") for tick in tax.get_yticklabels()]
    return axes


# pylint: disable=R0914, W0212, C0103, W0106
def plot_sequence(seq: Sequence, axes: (plt.Axes, ...) = None,
                  format_axes: bool = True,
                  add_legend: bool = True,
                  adc_yoffset: float = 0,
                  n_yticks: int = 5,
                  plot_center_lines: bool = True,
                  legend_position: str = "upper left"
                  ) -> plt.Figure:
    """ Plot RF, gradients and adc events into a(4, 1) axes grid. If for axes are specified
    as argument, plots are inserted there.

    :param seq: Instance of cmrseq.Sequence
    :param axes: (plt.Axes, plt.Axes, plt.Axes, plt.Axes)  (rf, gx, gy, gz) or a single instance
                    of plt.Axes if everything shall be plotted in the same axis
    :param format_axes: if true applies styling to the axes
    :param add_legend: if true adds legend to the first axis. If no axes are provided, this
                        is forced to be True
    :param adc_yoffset: determines the y-offset for adc-event markers
    :param n_yticks: determines the number of y ticks if format axes is True
    :param plot_center_lines: If True, adds vertical lines for rf-centers and adc-centers
    :param legend_position: Position of legend if it is added
    """
    if axes is None:
        f, axes = plt.subplots(4, 1, sharex='col')
        f.set_size_inches(6, 6)
        f.tight_layout()
        add_legend = True
    else:
        f = None

    single_axis = isinstance(axes, plt.Axes)
    if single_axis:
        rf_ax = axes.twinx()
        rf_ax.tick_params("y", colors="purple", direction="in")
        rf_ax.yaxis.set_label_position('left')
        rf_ax.yaxis.label.set_color('purple')
        rf_ax.yaxis.set_ticks_position('left')
        axes = [rf_ax, axes, axes, axes]

    # Plot RF
    t, rf_grid = seq.rf_to_grid()
    if rf_grid is not None:
        axes[0].plot(t, np.real(rf_grid) * 1000, color="purple", label="Re(RF)")
        axes[0].plot(t, np.imag(rf_grid) * 1000, color="purple", linestyle="--", label="Im(RF)")

    if plot_center_lines:
        rf_events = seq.rf_events
        if rf_events:  # [] == False
            [axes[0].axvline(t.m_as("ms"), linestyle='-', linewidth=1, color="purple", alpha=0.5)
             for (t, _) in rf_events]

    # Plot Gradients
    t, gradients = seq.gradients_to_grid()
    if gradients is not None:
        labels = ["Gx", "Gy", "Gz"]
        for idx, ax, gc in zip(range(3), axes[1:], gradients):
            ax.plot(t, gc, color=f"C{idx}", label=labels[idx])

    # Plot ADC
    for block in seq:
        if isinstance(block, ADC):
            sampling_times = block.adc_timing
            rect = patches.Rectangle((block.tmin.m_as("ms"), adc_yoffset-1),
                                     (block.tmax - block.tmin).m_as("ms"),
                                     2, linewidth=1.5, facecolor=(0, 0, 0, 0.1),
                                     edgecolor=(0., 0., 0., 0.2))
            if plot_center_lines:
                axes[0].axvline(block.adc_center.m_as("ms"), linestyle="--",
                                color=(234 / 256, 211 / 256, 168 / 256, 1.))
            axes[0].add_patch(rect)
            normed_phase = block.adc_phase / np.pi
            axes[0].vlines(sampling_times.m_as("ms"), adc_yoffset-0.75, adc_yoffset+0.75,
                           color="crimson", linewidth=1.5)
            axes[0].plot(sampling_times.m_as("ms"), normed_phase + adc_yoffset,
                         linestyle="-", color=(234 / 256, 211 / 256, 168 / 256, 1.), linewidth=4)

    # Create custom legend
    if add_legend:
        legend_handles = [patches.Rectangle((0, 0), 1, 1, facecolor="purple"),
                          plt.Line2D([0], [0], linestyle="-", color="purple"),
                          plt.Line2D([0], [0], linestyle="--", color="purple"),
                          plt.Line2D([0], [0], linestyle="-", color="C0"),
                          plt.Line2D([0], [0], linestyle="-", color="C1"),
                          plt.Line2D([0], [0], linestyle="-", color="C2"),
                          patches.Rectangle((0, 0), 1, 1, linewidth=1.5,
                                            facecolor=(0, 0, 0, 0.2), edgecolor=(0., 0., 0., 0.4)),
                          plt.Line2D([0], [0], color="crimson", marker="|", linewidth=0),
                          plt.Line2D([0], [0], linestyle="-", color=(234/256, 211/256, 168/256, 1.)),
                          plt.Line2D([0], [0], color="purple", marker="|", linewidth=0),
                          plt.Line2D([0], [0], color=(234 / 256, 211 / 256, 168 / 256, 1.), marker="|", linewidth=0),
                          plt.Line2D([0], [0], color="white", marker="|", linewidth=0, alpha=0)
                          ]
        legend_names = ["RF", r"$Re$", r"$Im$", "Gx", "Gy", "Gz", "ADC", "events",
                        "phase", "RF-centers", "ADC-centers", ""]
        legend = axes[0].legend(handles=legend_handles, labels=legend_names, ncol=4,
                                columnspacing=2, fontsize=10, handlelength=3, loc=legend_position)
        small_texts = [legend.get_texts()[i] for i in [1, 2, 7, 8]]
        [t.set_size(7) for t in small_texts]
        small_handles = [legend.legendHandles[i] for i in [1, 2, 7, 8]]
        [plt.setp(h, xdata=np.array([h.get_xdata()[-1] * 0.4, *h.get_xdata()[1:]]))
         for h in small_handles]

    if format_axes:
        [ax.set_ylabel(l) for ax, l in zip(axes, [r"RF [$\mu$T]", "G [mT/m]",
                                                  "G [mT/m]", "G [mT/m]"])]
        axes[-1].set_xlabel("Time [ms]")
        grad_range = np.array([-seq._system_specs.max_grad.m_as("mT/m"),
                                seq._system_specs.max_grad.m_as("mT/m")])
        rf_range = np.array([-seq._system_specs.rf_peak_power.m_as("uT"),
                                seq._system_specs.rf_peak_power.m_as("uT")])
        [ax.grid(True) for ax in axes]
        [ax.set_ylim(grad_range * 1.1) for ax in axes[1:]]
        [ax.set_yticks(np.linspace(*grad_range, n_yticks)) for ax in axes[1:]]
        [ax.yaxis.set_major_formatter(FormatStrFormatter('%3.2f')) for ax in axes]
        axes[0].set_ylim(rf_range * 1.1), axes[0].set_yticks(np.linspace(*rf_range, n_yticks))
        if single_axis:
            [tick.set_verticalalignment("bottom") for tick in axes[0].get_yticklabels()]
            [tick.set_verticalalignment("top") for tick in axes[1].get_yticklabels()]
            axes[0].set_ylabel("RF" + r"[$\mu$T]", labelpad=20)
    return f


# pylint: disable=R0914, W0212, C0103, W0106
def plot_kspace_2d(seq: Sequence, plot_raster_trajectory: bool = True,
                   k_axes: Tuple[int, int] = (0, 1), ax: plt.Axes = None,
                   format_axes: bool = True, markersize: int = 15) -> plt.Axes:
    """ 2D-scatter plot the trajectory of the sequence and its adc events

    :param seq:
    :param plot_raster_trajectory: if true plots the k-space points for all gradient raster points
    :param k_axes: determines which combination of (kx, ky, kz) to scatter plot
    :param ax: plt.Axis, if not None this is used to plot k-space
    :param format_axes:
    :param markersize:
    :return: axis used to plot
    """
    axes_labels = ["$k_x$", "$k_y$", "$k_z$"]
    ktot, kadc, _ = seq.calculate_kspace()
    if ax is None:
        _, ax = plt.subplots(1, 1)
        format_axes = True
    if plot_raster_trajectory:
        ax.plot(*ktot[k_axes, :], color=np.array([[41, 52, 98]]) / 255,
                label="Full Trajectory", alpha=0.4)
    if kadc is not None:
        ax.scatter(*kadc[k_axes, :], s=markersize, marker="x", c=np.array([[242, 76, 76]])/255,
                   label="Sampling events")

    if format_axes:
        ax.set_xlabel(axes_labels[k_axes[0]] + r" $[1/m]$")
        ax.set_ylabel(axes_labels[k_axes[1]] + r" $[1/m]$")
        ax.grid(True, alpha=0.5)
    return ax


# pylint: disable=R0914, W0212, C0103, W0106
def plot_kspace_3d(seq: Sequence, plot_raster_trajectory: bool = False,
                   axis = None, format_axis: bool = True, marker_kw: dict = None,
                   line_kw: dict = None) -> (plt.Figure, plt.Axes):
    """ 3D-scatter plot the trajectory of the sequence and its adc events

    :param seq:
    :param plot_raster_trajectory: if true plots the k-space points for all gradient raster points
    :param axis:
    :param format_axis:
    :param marker_kw: keyword arguments for sample-markers
    :param line_kw: keyword arguments for gradient trajectory line
    """
    if axis is None:
        fig, axis = plt.subplots(1, 1, subplot_kw={'projection': '3d'})

    if format_axis:
        axis.grid(True)
        axis.set_xlabel("$k_x$"), axis.set_ylabel("$k_y$"), axis.set_ylabel("$k_z$")

    if marker_kw is None:
        marker_kw = dict(s=2., marker="x", c="red")
    if line_kw is None:
        line_kw = dict(s=0.1, c="blue")

    ktot, kadc, _ = seq.calculate_kspace()
    if plot_raster_trajectory:
        axis.scatter(*ktot, **line_kw)
    axis.scatter(*kadc, **marker_kw)

    return axis


def plot_block_names(seq: Sequence, axis: plt.Axes, fontsize: float = 9):
    """ Plots a time for the given sequence, on which the names of all contained blocks are
    added at their corresponding start time

    :param seq:
    :param axis:
    :param fontsize:
    :return:
    """

    def plot_glyph(start, end, ypos, color, text, fontsize):
        axis.vlines([start, end], ypos - 0.75, ypos + 0.75, color=color, linewidth=2)
        axis.plot([start, end], [ypos, ypos], color=color, linewidth=2)
        axis.text(start + 0.05, ypos + 0.25, text, rotation=90, ha="left", fontsize=fontsize)

    block_types = [cmrseq.bausteine.RFPulse, cmrseq.bausteine.ADC, cmrseq.bausteine.Gradient]
    style_per_type = (dict(color="purple", ypos=4), dict(color="crimson", ypos=4),
                      dict(color="C0", ypos=0), dict(color="C1", ypos=-3),
                      dict(color="C2", ypos=-6))

    for idx, bn in enumerate(seq.blocks):
        block = seq.get_block(bn)
        type_idx = [isinstance(block, t) for t in block_types].index(True)
        if type_idx == 2:  # if gradient determine the major gradient axis
            max_axis = np.argmax(np.max(np.abs(block.gradients[1]), axis=1).m)
            type_idx += max_axis
        plot_glyph(block.tmin.m_as("ms"), block.tmax.m_as("ms"),
                   **style_per_type[type_idx], text=bn, fontsize=fontsize)
    axis.set_yticks(range(-8, 7))
    axis.set_yticklabels(
        ["", "", "$G_z$", "", "", "$G_y$", "", "", "$G_x$", "", "", "", "RF/ADC", "", ""])
    axis.grid(True)

def plot_gradient_spectra(seq: Sequence, directions: List[np.ndarray] = None, start_time: Quantity = None,
                          end_time: Quantity = None, ax: plt.Axes = None):
    """ Plots gradient sampling spectra for a given sequence along a list of directions. If no directions are given,
    plots along MPS
    :param seq: Instance of cmrseq.Sequence to plot spectra
    :param directions: List[np.ndarray of shape (3, )] directions to plot spectra along, default will plot MPS
    :param start_time: Quantity[Time] Start time of spectra calculation window
    :param end_time: Quantity[Time] End time of spectra calculation window
    :param ax: plt.Axes axis to place plots into, if not given creates and returns new figure
    """
    if ax is None:
        f, ax = plt.subplots(1, 1, )
        f.set_size_inches(6, 3)
    else:
        f = None

    if directions is not None:
        S, freq = cmrseq.utils.calculate_gradient_spectra(seq, directions=directions, start_time=start_time,
                                                          end_time=end_time)
        for s in S:
            ax.plot(freq.m_as('Hz'), s.m_as('mT^2/m^2*ms^4'))
    else:
        dirs = [np.array([1, 0, 0]), np.array([0, 1, 0]), np.array([0, 0, 1])]
        S, freq = cmrseq.utils.calculate_gradient_spectra(seq, directions=dirs, start_time=start_time,
                                                          end_time=end_time)
        ax.plot(freq.m_as('Hz'), S[0].m_as('mT^2/m^2*ms^4'))
        ax.plot(freq.m_as('Hz'), S[1].m_as('mT^2/m^2*ms^4'))
        ax.plot(freq.m_as('Hz'), S[2].m_as('mT^2/m^2*ms^4'))
        ax.legend(['M', 'P', 'S'])

    ax.set_xlim([0, 3000])
    ax.set_xlabel('Frequency, Hz')
    ax.set_ylabel(r'$S(\omega,t)$, $(mT/m*ms^2)^2$')

    return f