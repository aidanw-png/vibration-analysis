"""
Example application: bearing fault diagnostics.

Domain-specific code for the CWRU bearing dataset example, including
bearing geometry definitions, kinematic fault frequency calculation,
and dataset loading.
"""

from .cwru import load_cwru_dataset, CWRU_INVENTORY, FS
from .geometry import (
    bearing_fault_frequencies,
    SKF_6205_2RS_JEM,
    SKF_6203_2RS_JEM,
)