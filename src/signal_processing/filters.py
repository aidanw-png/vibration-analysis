"""
Digital filter design and application.

Zero-phase Butterworth filters (bandpass, lowpass, highpass) for
preprocessing vibration signals.
"""

import numpy as np
from scipy.signal import butter, sosfiltfilt


def bandpass_filter(signal, fs, lowcut, highcut, order=4):
    """
    Apply a zero-phase Butterworth bandpass filter to a signal.

    Filtering is performed using second-order sections (SOS) for
    numerical stability, and applied forward and backward via
    `sosfiltfilt` to eliminate phase distortion. The effective filter
    order is therefore twice the design order.

    Parameters
    ----------
    signal : array_like
        1D real-valued time-series signal.
    fs : float
        Sampling frequency in Hz.
    lowcut, highcut : float
        Lower and upper passband edges in Hz.
    order : int, optional
        Filter design order. Default 4 is standard for vibration work.
        Higher orders give sharper rolloff but increase numerical risk;
        SOS representation mitigates this but very high orders (>8)
        are rarely justified.

    Returns
    -------
    filtered : ndarray
        Bandpass-filtered signal, same length as input, with zero
        phase distortion.

    Notes
    -----
    Butterworth filters are the standard choice for vibration
    preprocessing because they have maximally flat magnitude response
    in the passband and no ripple. Chebyshev and elliptic alternatives
    give steeper rolloff but introduce passband ripple that distorts
    amplitude information — undesirable when the downstream step is
    envelope extraction.
    """
    nyquist = fs / 2
    sos = butter(
        order,
        [lowcut / nyquist, highcut / nyquist],
        btype='band',
        output='sos',
    )
    return sosfiltfilt(sos, signal)