"""
Wave kinematic module
"""
import sys

from _WaveKinematic import set_logger_level, add_logger_callback
from . import waveKinematic

mod = sys.modules[__name__]

for name in waveKinematic.availableWaveKinematic :
    setattr( mod , name , getattr( waveKinematic , name ) )

from .variableBathymetry import VariableBathymetry , check_second_order_flat
