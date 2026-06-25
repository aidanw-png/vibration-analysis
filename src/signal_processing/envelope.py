"""
Envelope extraction via the Hilbert transform.

Computes the amplitude envelope of an oscillating signal, used in
envelope analysis for demodulating amplitude-modulated carriers.
"""

import numpy as np
from scipy.signal import hilbert


def compute_envelope(signal):
    """
    Compute the amplitude envelope of a signal via the Hilbert transform.

    The Hilbert transform constructs an analytic signal whose magnitude
    is the instantaneous amplitude envelope of the input. For an
    amplitude-modulated carrier signal x(t) = A(t)·cos(2πf_c·t), this
    recovers A(t) — the slowly-varying modulation pattern — with the
    high-frequency carrier removed.

    Parameters
    ----------
    signal : array_like
        Real-valued 1D signal. Typically bandpass-filtered around a
        carrier frequency before this function is applied, so that
        the resulting envelope reflects modulation of that specific
        carrier rather than the full broadband signal.

    Returns
    -------
    envelope : ndarray
        Amplitude envelope, same length as input, always non-negative.

    Notes
    -----
    `scipy.signal.hilbert` returns the full analytic signal (complex-
    valued), not the Hilbert transform alone. Taking `np.abs` of the
    analytic signal yields the envelope. This is a naming quirk worth
    knowing — the function is named after the underlying operation
    but returns the more useful analytic signal directly.

    The envelope is a strictly positive signal with a non-zero mean.
    When computing its spectrum, subtract the mean first to avoid a
    large DC peak obscuring the modulation frequencies.
    """
    analytic = hilbert(signal)
    return np.abs(analytic)


def envelope_spectrum(signal, fs, welch_psd_fn, nperseg=4096):
    """
    Compute the AC-coupled envelope spectrum of a signal.

    Convenience function combining envelope extraction (via the Hilbert
    transform), DC removal (mean subtraction), and power spectral density
    estimation. The resulting spectrum reveals modulation frequencies
    that are otherwise obscured by the DC component of the strictly-
    positive envelope.

    Parameters
    ----------
    signal : array_like
        1D real-valued signal — typically a bandpass-filtered carrier.
    fs : float
        Sampling frequency in Hz.
    welch_psd_fn : callable
        Function for computing the Welch PSD. Must have the signature
        welch_psd_fn(signal, fs, nperseg=...) and return (freqs, psd).
        Injected as a parameter to keep this module independent of
        spectral.py.
    nperseg : int, optional
        Welch segment length. Default 4096.

    Returns
    -------
    freqs : ndarray
        Frequency axis in Hz.
    psd : ndarray
        Envelope power spectral density.
    """
    envelope = compute_envelope(signal)
    envelope_ac = envelope - envelope.mean()
    return welch_psd_fn(envelope_ac, fs=fs, nperseg=nperseg)