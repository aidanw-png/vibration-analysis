"""
Case Western Reserve University bearing dataset loader.

File inventory and loading utilities for the CWRU 12 kHz drive-end
accelerometer data. See https://engineering.case.edu/bearingdatacenter
for the dataset.
"""

from pathlib import Path
from scipy.io import loadmat


# ----------------------------------------------------------------------
# Dataset inventory
# ----------------------------------------------------------------------
#
# Each entry describes one operating condition. The 'variable' field is
# the variable name inside the .mat file, which follows CWRU's internal
# file numbering convention rather than the descriptive filename.
#
# All four files are at 1772 rpm under 1 HP load, with a 0.007" fault
# diameter on the affected component.

FS = 12000  # Drive-end accelerometer sampling rate in Hz

CWRU_INVENTORY = {
    'Healthy': {
        'filename': 'Normal_1.mat',
        'variable': 'X098_DE_time',
        'rpm':      1772,
        'fault':    'None',
    },
    'Inner Race': {
        'filename': 'IR007_1.mat',
        'variable': 'X106_DE_time',
        'rpm':      1772,
        'fault':    '0.007" inner race defect',
    },
    'Ball': {
        'filename': 'B007_1.mat',
        'variable': 'X119_DE_time',
        'rpm':      1772,
        'fault':    '0.007" rolling element defect',
    },
    'Outer Race': {
        'filename': 'OR007@6_1.mat',
        'variable': 'X131_DE_time',
        'rpm':      1772,
        'fault':    '0.007" outer race defect at 6 o\'clock',
    },
}


# ----------------------------------------------------------------------
# Loader
# ----------------------------------------------------------------------

def load_cwru_dataset(data_dir, conditions=None):
    """
    Load CWRU bearing dataset signals and metadata.

    Parameters
    ----------
    data_dir : str or Path
        Path to the directory containing the CWRU .mat files.
    conditions : list of str, optional
        Which conditions to load (subset of CWRU_INVENTORY keys). If None,
        all four conditions are loaded.

    Returns
    -------
    signals : dict
        Mapping from condition name to 1D numpy array of acceleration samples.
    metadata : dict
        Mapping from condition name to per-condition metadata
        ('filename', 'variable', 'rpm', 'fault', 'n_samples', 'duration_s').

    Raises
    ------
    FileNotFoundError
        If any requested file is missing from data_dir.
    KeyError
        If the expected variable is not present in a loaded .mat file.

    Notes
    -----
    All signals are sampled at 12 kHz on the drive-end accelerometer. See
    the module-level constant CWRU_INVENTORY for the file inventory.
    """
    data_dir = Path(data_dir)
    if conditions is None:
        conditions = list(CWRU_INVENTORY.keys())

    signals = {}
    metadata = {}

    for condition in conditions:
        info = CWRU_INVENTORY[condition]
        path = data_dir / info['filename']

        if not path.exists():
            raise FileNotFoundError(
                f"CWRU file not found: {path}. "
                f"Download from https://engineering.case.edu/bearingdatacenter"
            )

        mat = loadmat(path)
        if info['variable'] not in mat:
            raise KeyError(
                f"Variable '{info['variable']}' not found in {path}. "
                f"Available variables: {[k for k in mat if not k.startswith('__')]}"
            )

        signal = mat[info['variable']].flatten()
        signals[condition] = signal

        metadata[condition] = {
            **info,
            'n_samples':  len(signal),
            'duration_s': len(signal) / FS,
        }

    return signals, metadata