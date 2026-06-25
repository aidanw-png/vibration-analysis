"""
Bearing geometry and kinematic fault frequencies.

Standard bearing definitions and the calculation of ball pass frequencies
(BPFO, BPFI), ball spin frequency (BSF), and fundamental train frequency
(FTF) from bearing geometry and shaft speed.
"""

import numpy as np


# ----------------------------------------------------------------------
# Standard bearing geometries
# ----------------------------------------------------------------------
#
# Dimensions in inches as published by manufacturers. Formulas only
# depend on the ratio d/D so the units cancel — but keeping consistent
# units avoids confusion. Source URLs document the original references.

SKF_6205_2RS_JEM = {
    'name':              'SKF 6205-2RS JEM',
    'n_balls':           9,
    'ball_diameter_in':  0.3126,
    'pitch_diameter_in': 1.537,
    'contact_angle_deg': 0.0,
    'source':            'https://engineering.case.edu/bearingdatacenter/bearing-information',
}

SKF_6203_2RS_JEM = {
    'name':              'SKF 6203-2RS JEM',
    'n_balls':           9,
    'ball_diameter_in':  0.2656,
    'pitch_diameter_in': 1.122,
    'contact_angle_deg': 0.0,
    'source':            'https://engineering.case.edu/bearingdatacenter/bearing-information',
}


# ----------------------------------------------------------------------
# Fault frequency calculation
# ----------------------------------------------------------------------

def bearing_fault_frequencies(rpm, bearing):
    """
    Compute characteristic bearing fault frequencies from geometry and speed.

    Returns the four classical kinematic fault frequencies for a rolling
    element bearing: ball pass frequency inner race (BPFI), ball pass
    frequency outer race (BPFO), ball spin frequency (BSF), and
    fundamental train frequency (FTF, the cage rotation rate).

    Parameters
    ----------
    rpm : float
        Shaft speed in revolutions per minute.
    bearing : dict
        Bearing geometry dictionary with keys 'n_balls',
        'ball_diameter_in', 'pitch_diameter_in', 'contact_angle_deg'.
        See module-level constants (e.g. SKF_6205_2RS_JEM) for examples.

    Returns
    -------
    freqs : dict
        Frequencies in Hz:
            'f_shaft' : shaft rotation frequency
            'BPFI'    : ball pass frequency, inner race
            'BPFO'    : ball pass frequency, outer race
            'BSF'     : ball spin frequency (impact convention — twice
                        the ball rotational rate, since a ball defect
                        contacts both races per element revolution)
            'FTF'     : fundamental train (cage) frequency

    Notes
    -----
    The BSF returned here uses the **impact** convention, which matches
    the published rolling-element coefficient from manufacturers and
    is the diagnostically relevant rate at which a ball defect strikes
    a race. Some references use the rotational convention (half this
    value); be aware of the inconsistency when comparing to literature.

    These are kinematic (no-slip) frequencies. Real bearings have some
    rolling-element slip, so observed fault frequencies are typically
    within 1–2% of theoretical for race faults and up to 5% for ball
    faults.
    """
    f_r = rpm / 60.0
    n = bearing['n_balls']
    d = bearing['ball_diameter_in']
    D = bearing['pitch_diameter_in']
    alpha = np.radians(bearing['contact_angle_deg'])

    ratio = (d / D) * np.cos(alpha)

    return {
        'f_shaft': f_r,
        'BPFI':    (n / 2) * f_r * (1 + ratio),
        'BPFO':    (n / 2) * f_r * (1 - ratio),
        'BSF':     (D / d) * f_r * (1 - ratio**2),
        'FTF':     (f_r / 2) * (1 - ratio),
    }