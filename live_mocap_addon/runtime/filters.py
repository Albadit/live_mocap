"""
Smoothing filters and confidence gating for motion data.
"""

from mathutils import Vector, Quaternion
from typing import Optional, Union


class SmoothingFilter:
    """Exponential weighted moving average (EWMA) filter."""
    
    def __init__(self, alpha: float = 0.5):
        """
        Initialize filter.
        
        Args:
            alpha: Smoothing factor (0=no smoothing, 1=max smoothing)
                   Internally converted to lerp factor
        """
        self.alpha = 1.0 - alpha  # Convert to lerp factor
        self.prev_value: Optional[Union[Vector, Quaternion, float]] = None
    
    def filter(self, value: Union[Vector, Quaternion, float]) -> Union[Vector, Quaternion, float]:
        """
        Apply smoothing to a value.
        
        Args:
            value: Value to smooth (Vector, Quaternion, or float)
        
        Returns:
            Smoothed value
        """
        if self.prev_value is None:
            self.prev_value = value.copy() if hasattr(value, 'copy') else value
            return value
        
        # Apply lerp/slerp based on type
        if isinstance(value, Vector):
            smoothed = self.prev_value.lerp(value, self.alpha)
        elif isinstance(value, Quaternion):
            smoothed = self.prev_value.slerp(value, self.alpha)
        else:
            smoothed = self.prev_value * (1 - self.alpha) + value * self.alpha
        
        self.prev_value = smoothed.copy() if hasattr(smoothed, 'copy') else smoothed
        return smoothed
    
    def reset(self):
        """Reset the filter."""
        self.prev_value = None


class ConfidenceGate:
    """Gate values based on confidence threshold."""
    
    def __init__(self, min_confidence: float = 0.5):
        """
        Initialize confidence gate.
        
        Args:
            min_confidence: Minimum confidence to accept values
        """
        self.min_confidence = min_confidence
        self.last_valid_value = None
    
    def filter(self, value, confidence: float):
        """
        Filter value based on confidence.
        
        Args:
            value: Value to filter
            confidence: Confidence level [0, 1]
        
        Returns:
            Value if confidence >= threshold, else last valid value or None
        """
        if confidence >= self.min_confidence:
            self.last_valid_value = value
            return value
        else:
            return self.last_valid_value
    
    def reset(self):
        """Reset the gate."""
        self.last_valid_value = None


class FootLockFilter:
    """Simple foot locking based on height threshold."""
    
    def __init__(self, threshold: float = 0.05):
        """
        Initialize foot lock filter.
        
        Args:
            threshold: Height variance threshold for locking
        """
        self.threshold = threshold
        self.locked_height = None
        self.is_locked = False
    
    def filter(self, foot_position: Vector, velocity: float = 0.0) -> Vector:
        """
        Apply foot locking.
        
        Args:
            foot_position: Current foot position
            velocity: Optional velocity for better locking detection
        
        Returns:
            Filtered foot position (locked if threshold met)
        """
        if self.threshold <= 0:
            return foot_position  # Disabled
        
        foot_height = foot_position.z
        
        # Check if foot should be locked (near ground with low velocity)
        if foot_height < self.threshold and velocity < 0.1:
            if not self.is_locked:
                self.locked_height = foot_height
                self.is_locked = True
        else:
            self.is_locked = False
            self.locked_height = None
        
        # Apply lock
        if self.is_locked and self.locked_height is not None:
            locked_pos = foot_position.copy()
            locked_pos.z = self.locked_height
            return locked_pos
        
        return foot_position
    
    def reset(self):
        """Reset the filter."""
        self.locked_height = None
        self.is_locked = False


class MultiFilter:
    """Combines multiple filters for a single value."""
    
    def __init__(self, smoothing_alpha: float = 0.5, 
                 min_confidence: float = 0.5,
                 foot_lock_threshold: float = 0.0):
        """
        Initialize multi-filter.
        
        Args:
            smoothing_alpha: Smoothing factor
            min_confidence: Minimum confidence threshold
            foot_lock_threshold: Foot lock threshold (0=disabled)
        """
        self.smoothing = SmoothingFilter(smoothing_alpha)
        self.confidence_gate = ConfidenceGate(min_confidence)
        self.foot_lock = FootLockFilter(foot_lock_threshold) if foot_lock_threshold > 0 else None
    
    def filter_position(self, position: Vector, confidence: float = 1.0, 
                       is_foot: bool = False, velocity: float = 0.0) -> Optional[Vector]:
        """
        Apply all position filters.
        
        Args:
            position: Position to filter
            confidence: Confidence level
            is_foot: Whether this is a foot position (for foot locking)
            velocity: Velocity for foot locking
        
        Returns:
            Filtered position or None if rejected
        """
        # Confidence gating
        filtered = self.confidence_gate.filter(position, confidence)
        if filtered is None:
            return None
        
        # Smoothing
        filtered = self.smoothing.filter(filtered)
        
        # Foot locking
        if is_foot and self.foot_lock is not None:
            filtered = self.foot_lock.filter(filtered, velocity)
        
        return filtered
    
    def filter_rotation(self, rotation: Quaternion, confidence: float = 1.0) -> Optional[Quaternion]:
        """
        Apply rotation filters (confidence + smoothing).
        
        Args:
            rotation: Rotation to filter
            confidence: Confidence level
        
        Returns:
            Filtered rotation or None if rejected
        """
        # Confidence gating
        filtered = self.confidence_gate.filter(rotation, confidence)
        if filtered is None:
            return None
        
        # Smoothing
        filtered = self.smoothing.filter(filtered)
        
        return filtered
    
    def reset(self):
        """Reset all filters."""
        self.smoothing.reset()
        self.confidence_gate.reset()
        if self.foot_lock:
            self.foot_lock.reset()
