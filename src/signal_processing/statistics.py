"""
Time-domain statistics for vibration signals.

Standard scalar indicators: RMS, kurtosis, crest factor. Peak detection
within a specified frequency window.
"""

import numpy as np
from scipy.stats import kurtosis as scipy_kurtosis


def time_domain_statistics(signal, fs):
    """
    Compute standard time-domain statistical indicators for a vibration signal.

    Parameters
    ----------
    signal : array_like
        1D real-valued time-series signal.
    fs : float
        Sampling frequency in Hz.

    Returns
    -------
    stats : dict
        Dictionary of scalar indicators:
            'n_samples'     : int, number of samples
            'duration_s'    : float, record duration in seconds
            'mean'          : float, signal mean
            'std'           : float, signal standard deviation
            'min'           : float, signal minimum
            'max'           : float, signal maximum
            'rms'           : float, root mean square
            'peak'          : float, maximum absolute value
            'crest_factor'  : float, peak / rms (unitless)
            'kurtosis'      : float, classical kurtosis (Gaussian = 3)

    Notes
    -----
    Kurtosis is returned in the classical (non-Fisher) convention where
    a Gaussian distribution gives a value of 3. Impulsive signals have
    kurtosis > 3; bearing fault signals typically show values of 5–10
    or higher in the time domain.

    Crest factor (peak / RMS) is a record-length-dependent statistic.
    Longer records have more opportunities to capture extreme values
    and therefore higher crest factors. Compare across signals of
    similar duration for meaningful results.
    """
    signal = np.asarray(signal)
    rms = np.sqrt(np.mean(signal**2))
    peak = np.max(np.abs(signal))

    return {
        'n_samples':    len(signal),
        'duration_s':   len(signal) / fs,
        'mean':         np.mean(signal),
        'std':          np.std(signal),
        'min':          np.min(signal),
        'max':          np.max(signal),
        'rms':          rms,
        'peak':         peak,
        'crest_factor': peak / rms,
        'kurtosis':     scipy_kurtosis(signal, fisher=False),
    }


def peak_to_noise_ratio(freqs, psd, peak_freq, search_halfwidth_hz=20):
    """
    Compute the peak-to-noise ratio around a target frequency.

    Finds the maximum PSD value within ±search_halfwidth_hz of
    peak_freq, and divides by the median PSD value in that band
    (excluding the top 20% of bins, which captures the peak and its
    immediate neighbours). The median provides a robust noise floor
    estimate that is not contaminated by the peak itself.

    Parameters
    ----------
    freqs : ndarray
        Frequency axis in Hz.
    psd : ndarray
        Power spectral density values.
    peak_freq : float
        Target frequency in Hz at which a peak is expected.
    search_halfwidth_hz : float, optional
        Half-width of the search band in Hz. Default 20.

    Returns
    -------
    ratio : float
        Peak PSD value divided by median noise floor (linear, not dB).
    """
    band_mask = np.abs(freqs - peak_freq) <= search_halfwidth_hz
    band_psd = psd[band_mask]
    peak_val = band_psd.max()
    noise_floor = np.median(np.sort(band_psd)[:int(0.8 * len(band_psd))])
    return peak_val / noise_floor


def find_fault_peak(freqs, psd, theoretical_freq, tolerance=0.05,
                    snr_threshold_db=6.0):
    """
    Locate and characterise a spectral peak near a theoretical frequency.

    Searches within a tolerance window around the theoretical frequency
    for the highest PSD bin, then reports the measured frequency, the
    deviation from theoretical, and the peak-to-noise ratio expressed
    in decibels. A detection flag indicates whether the peak exceeds
    a confidence threshold.

    Parameters
    ----------
    freqs : ndarray
        Frequency axis in Hz from a Welch PSD or envelope spectrum.
    psd : ndarray
        PSD values corresponding to `freqs`.
    theoretical_freq : float
        Theoretical (predicted) frequency of the peak in Hz.
    tolerance : float, optional
        Search half-width as a fraction of theoretical_freq. Default
        0.05 (i.e. ±5%), which accommodates typical rolling-element
        slip in real bearings without admitting unrelated peaks.
    snr_threshold_db : float, optional
        SNR threshold above which a peak is considered confidently
        detected. Default 6 dB (peak twice the noise floor).

    Returns
    -------
    result : dict
        Keys:
            'f_theoretical' : float, the input theoretical frequency
            'f_measured'    : float, frequency of the maximum bin
            'error_hz'      : float, f_measured - f_theoretical
            'error_pct'     : float, percentage deviation
            'peak_psd'      : float, PSD value at the peak
            'snr_db'        : float, peak-to-noise ratio in dB
            'detected'      : bool, True if snr_db > snr_threshold_db
    """
    halfwidth = tolerance * theoretical_freq
    mask = np.abs(freqs - theoretical_freq) <= halfwidth
    band_freqs = freqs[mask]
    band_psd = psd[mask]

    peak_idx = np.argmax(band_psd)
    f_measured = band_freqs[peak_idx]
    peak_psd = band_psd[peak_idx]

    error_hz = f_measured - theoretical_freq
    error_pct = 100 * error_hz / theoretical_freq

    snr = peak_to_noise_ratio(freqs, psd, theoretical_freq)
    snr_db = 10 * np.log10(snr)

    return {
        'f_theoretical': theoretical_freq,
        'f_measured':    f_measured,
        'error_hz':      error_hz,
        'error_pct':     error_pct,
        'peak_psd':      peak_psd,
        'snr_db':        snr_db,
        'detected':      bool(snr_db > snr_threshold_db),
    }