"""
Standardised plotting helpers for vibration analysis.

Consistent figure styling, axis conventions, and overlay patterns for
spectra, time series, and diagnostic comparisons.
"""

import matplotlib.pyplot as plt
import numpy as np


def plot_spectrum_panels(spectra, xlim=None, ylabel='PSD',
                         overlays=None, overlay_colors=None,
                         title=None, figsize=(12, 8), log_y=True):
    """
    Plot a stack of spectra as a multi-panel figure with shared axes.

    Each panel shows one spectrum, labelled by its dictionary key.
    Optional vertical-line overlays mark theoretical frequencies of
    interest (e.g. bearing fault frequencies, structural modes).

    Parameters
    ----------
    spectra : dict
        Mapping from panel label to (freqs, spectrum) tuple. Each
        spectrum is plotted in its own subplot in dictionary order.
    xlim : tuple of (float, float), optional
        Frequency axis limits in Hz. If None, uses matplotlib defaults.
    ylabel : str, optional
        Y-axis label, applied to all panels via a single figure-level
        label on the left.
    overlays : dict of dict, optional
        Per-panel overlay frequencies. Outer keys must match the
        spectra keys; inner keys are labels (e.g. 'BPFO'), inner
        values are frequencies in Hz. Panels without an overlay entry
        get no vertical lines.
    overlay_colors : dict, optional
        Mapping from overlay label root to colour. Labels with '×'
        prefixes (e.g. '2×BPFO') use the root after the last '×'.
        Unmatched labels fall back to gray.
    title : str, optional
        Figure-level suptitle.
    figsize : tuple, optional
        Figure size in inches.
    log_y : bool, optional
        Whether to use logarithmic y-axis. Default True (appropriate
        for spectral data spanning multiple orders of magnitude).

    Returns
    -------
    fig, axes : matplotlib Figure and array of Axes
        Returned so the caller can post-process — set custom titles,
        save to a specific path, or modify particular axes.
    """
    n_panels = len(spectra)
    fig, axes = plt.subplots(n_panels, 1, figsize=figsize,
                             sharex=True, sharey=True)

    if n_panels == 1:
        axes = [axes]  # ensure axes is iterable for the single-panel case

    overlay_colors = overlay_colors or {}

    for ax, (label, (freqs, spectrum)) in zip(axes, spectra.items()):
        if log_y:
            ax.semilogy(freqs, spectrum, linewidth=0.7, color='black')
        else:
            ax.plot(freqs, spectrum, linewidth=0.7, color='black')

        if overlays and label in overlays:
            for overlay_label, f in overlays[label].items():
                base = overlay_label.split('×')[-1] if '×' in overlay_label else overlay_label
                color = overlay_colors.get(base, 'gray')
                ax.axvline(f, color=color, linestyle='--',
                           linewidth=1.0, alpha=0.7)
                ax.text(f, ax.get_ylim()[1] * 0.5, overlay_label,
                        rotation=90, ha='right', va='top',
                        fontsize=8, color=color)

        ax.set_ylabel(label, rotation=0, ha='right', va='center', fontsize=10)
        if xlim is not None:
            ax.set_xlim(xlim)
        ax.grid(True, which='both', alpha=0.3)

    axes[-1].set_xlabel('Frequency (Hz)')
    fig.text(0.02, 0.5, ylabel, rotation=90, va='center')
    if title is not None:
        fig.suptitle(title, fontsize=12, y=0.995)
    fig.tight_layout()

    return fig, axes