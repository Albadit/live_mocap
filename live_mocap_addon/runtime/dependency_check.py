"""
Dependency checking for OpenCV and MediaPipe.
Uses Rokoko-style library manager for installation.
"""

import sys
from typing import Dict, Tuple


# Required libraries for the addon
REQUIRED_LIBRARIES = [
    "opencv-python",
    "mediapipe"
]

# Map package names to import names
PACKAGE_IMPORT_MAP = {
    "opencv-python": "cv2",
    "mediapipe": "mediapipe"
}


class DependencyStatus:
    """Tracks dependency availability and error messages."""
    
    def __init__(self):
        self._available: Dict[str, bool] = {
            "cv2": False,
            "mediapipe": False
        }
        self._versions: Dict[str, str] = {}
        self._error_msg = ""
    
    def check(self) -> bool:
        """
        Check if all required dependencies are available.
        
        Returns:
            True if all dependencies are available
        """
        errors = []
        
        # Check OpenCV
        try:
            import cv2
            self._available["cv2"] = True
            self._versions["cv2"] = cv2.__version__
        except ImportError:
            errors.append("opencv-python")
            self._available["cv2"] = False
        
        # Check MediaPipe
        try:
            import mediapipe
            self._available["mediapipe"] = True
            self._versions["mediapipe"] = mediapipe.__version__
        except ImportError:
            errors.append("mediapipe")
            self._available["mediapipe"] = False
        
        # Build error message
        if errors:
            self._error_msg = f"Missing: {', '.join(errors)}"
        else:
            self._error_msg = ""
        
        return all(self._available.values())
    
    def is_available(self, package: str) -> bool:
        """Check if a specific package is available."""
        return self._available.get(package, False)
    
    def get_version(self, package: str) -> str:
        """Get version of a specific package."""
        return self._versions.get(package, "unknown")
    
    def get_error_message(self) -> str:
        """Get the error message for missing dependencies."""
        return self._error_msg
    
    def get_install_instructions(self) -> str:
        """Get installation instructions for missing dependencies."""
        python_exe = sys.executable
        
        msg = "Install missing dependencies:\n\n"
        
        if not self._available["cv2"]:
            msg += f'  OpenCV:\n    "{python_exe}" -m pip install opencv-python\n\n'
        
        if not self._available["mediapipe"]:
            msg += f'  MediaPipe:\n    "{python_exe}" -m pip install mediapipe\n\n'
        
        msg += "Restart Blender after installation."
        return msg


# Global instance
_dependency_status = DependencyStatus()


def check_dependencies() -> bool:
    """
    Check all dependencies.
    
    Returns:
        True if all dependencies are available
    """
    return _dependency_status.check()


def all_dependencies_available() -> bool:
    """
    Check if all dependencies are currently available.
    
    Returns:
        True if all dependencies are available
    """
    return all(_dependency_status._available.values())


def get_error_message() -> str:
    """Get error message for missing dependencies."""
    return _dependency_status.get_error_message()


def get_install_instructions() -> str:
    """Get installation instructions."""
    return _dependency_status.get_install_instructions()


def get_dependency_info() -> Dict[str, Tuple[bool, str]]:
    """
    Get detailed dependency information.
    
    Returns:
        Dict mapping package name to (available, version) tuple
    """
    return {
        pkg: (
            _dependency_status.is_available(pkg),
            _dependency_status.get_version(pkg)
        )
        for pkg in ["cv2", "mediapipe"]
    }


def safe_import_cv2():
    """
    Safely import cv2 with error handling.
    
    Returns:
        cv2 module or None if not available
    """
    try:
        import cv2
        return cv2
    except ImportError:
        return None


def safe_import_mediapipe():
    """
    Safely import mediapipe with error handling.
    
    Returns:
        mediapipe module or None if not available
    """
    try:
        import mediapipe
        return mediapipe
    except ImportError:
        return None
