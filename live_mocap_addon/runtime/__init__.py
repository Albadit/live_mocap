"""
Runtime package for live capture, tracking, and retargeting.
"""

from . import library_manager
from . import dependency_check
from . import capture
from . import trackers
from . import retarget
from . import mapping
from . import recording
from . import filters


def initialize():
    """Initialize runtime systems."""
    dependency_check.check_dependencies()


def cleanup():
    """Cleanup runtime systems."""
    pass


__all__ = [
    'library_manager',
    'dependency_check',
    'capture',
    'trackers',
    'retarget',
    'mapping',
    'recording',
    'filters',
    'initialize',
    'cleanup'
]
