"""
Octave and third-octave band analysis.

Converts power spectral densities into standardised band levels per
IEC 61260 / ISO 266, for compliance reporting against standards such
as ISO 10816 (machinery) and AS 2670 (human exposure).
"""

import numpy as np


# Reference vibration acceleration for dB conversion, per ISO 1683:
# 10^-6 m/s². Levels are L = 10·log10(a²/a_ref²).
A_REF = 1e-6  # m/s²


def third_octave_centres(f_min=12.5, f_max=12500):
    """
    Generate standard third-octave band centre frequencies per IEC 61260.

    Returns the preferred series of centre frequencies between f_min and
    f_max, where each centre is 10^(n/10) Hz rounded to standard values.

    Parameters
    ----------
    f_min, f_max : float, optional
        Lowest and highest centre frequencies to include, in Hz.
        Defaults span the standard third-octave range.

    Returns
    -------
    centres : ndarray
        Standardised third-octave centre frequencies in Hz.
    """
    # Standard third-octave preferred frequencies from IEC 61260
    preferred = np.array([
        12.5, 16, 20, 25, 31.5, 40, 50, 63, 80, 100,
        125, 160, 200, 250, 315, 400, 500, 630, 800, 1000,
        1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000,
        12500,
    ])
    return preferred[(preferred >= f_min) & (preferred <= f_max)]


def third_octave_band_levels(freqs, psd, centres=None, reference=A_REF):
    """
    Convert a PSD into third-octave band levels.

    For each centre frequency, integrates the PSD across the band edges
    at ±1/6 octave (a frequency ratio of 2^(1/3) across the full band),
    yielding the band's mean-square value. Converts to a level in dB
    relative to the reference.

    Parameters
    ----------
    freqs : ndarray
        Frequency axis of the input PSD, in Hz.
    psd : ndarray
        Power spectral density in (signal units)^2 / Hz.
    centres : ndarray, optional
        Third-octave centre frequencies to compute. If None (default),
        uses `third_octave_centres()` over the range of `freqs`.
    reference : float, optional
        Reference value for dB conversion. Default 1e-6 m/s² per
        ISO 1683. Use the appropriate reference for your signal units.

    Returns
    -------
    centres : ndarray
        Centre frequencies in Hz.
    levels_db : ndarray
        Band levels in dB re reference.

    Notes
    -----
    The integration uses simple summation weighted by frequency spacing,
    which assumes uniform PSD bin spacing (as produced by Welch's method).
    Bands containing fewer than one PSD bin will return -inf dB.
    """
    if centres is None:
        centres = third_octave_centres(freqs.min(), freqs.max())

    # Band edges at the standard ±1/6 octave from centre
    edge_factor = 2 ** (1/6)
    lower_edges = centres / edge_factor
    upper_edges = centres * edge_factor

    # Frequency resolution
    df = freqs[1] - freqs[0]

    levels_db = np.full_like(centres, -np.inf, dtype=float)

    for i, (f_lo, f_hi) in enumerate(zip(lower_edges, upper_edges)):
        mask = (freqs >= f_lo) & (freqs < f_hi)
        if mask.any():
            band_power = psd[mask].sum() * df
            if band_power > 0:
                levels_db[i] = 10 * np.log10(band_power / reference**2)

    return centres, levels_db