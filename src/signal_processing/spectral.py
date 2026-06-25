"""
Spectral analysis utilities.

Power spectral density estimation via Welch's method, and single-sided
amplitude spectra via the discrete Fourier transform. Domain-agnostic.
"""

import numpy as np
from scipy.signal import welch as scipy_welch


def welch_psd(signal, fs, nperseg=4096, noverlap=None, window='hann'):
    """
    Estimate the power spectral density of a signal using Welch's method.

    Welch's method divides the signal into overlapping segments, applies
    a window function to each, computes the periodogram of each, and
    averages the results. This trades frequency resolution for variance
    reduction, producing a much smoother spectrum than a single-shot FFT.

    Parameters
    ----------
    signal : array_like
        1D real-valued time-series signal.
    fs : float
        Sampling frequency in Hz.
    nperseg : int, optional
        Segment length in samples. Frequency resolution is fs/nperseg.
        Default 4096 is a sensible starting point but should be chosen
        based on the frequency features the user needs to resolve.
    noverlap : int, optional
        Samples of overlap between consecutive segments. If None (default),
        50% overlap is used (nperseg // 2).
    window : str, optional
        Window function name. Default 'hann'. Other useful options:
            'hamming' - similar properties, marginally different shape
            'flattop' - accurate amplitude reading of discrete tones
            'boxcar'  - no window (raw periodogram, leakage-prone)

    Returns
    -------
    freqs : ndarray
        Frequency axis in Hz, length nperseg // 2 + 1, from 0 to fs/2.
    psd : ndarray
        Power spectral density in (signal units)^2 / Hz.

    Notes
    -----
    Frequency resolution Δf = fs / nperseg. Choose nperseg so that Δf
    is comfortably smaller than the spacing between spectral features
    of interest. A general rule of thumb is Δf ≤ (feature spacing) / 4.

    The number of averaged segments scales as N / nperseg with 50%
    overlap, so larger nperseg gives finer resolution but fewer segments
    averaged. With fewer than ~10 segments the spectrum becomes noticeably
    noisy; with more than ~100 the additional averaging is wasted.
    """
    if noverlap is None:
        noverlap = nperseg // 2

    freqs, psd = scipy_welch(
        signal,
        fs=fs,
        nperseg=nperseg,
        noverlap=noverlap,
        window=window,
    )
    return freqs, psd