"""
Fault Localization Package.
"""
from .fault_localizer import FaultLocalizer

localizer = FaultLocalizer()

__all__ = ["FaultLocalizer", "localizer"]
