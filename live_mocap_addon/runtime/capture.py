"""
Camera capture management using OpenCV.
"""

from typing import Optional, Tuple
import time

from ..utils.logging_utils import get_logger


class CameraCapture:
    """Manages webcam capture with OpenCV."""
    
    def __init__(self, camera_index: int = 0, target_fps: int = 30):
        """
        Initialize camera capture.
        
        Args:
            camera_index: Webcam device index
            target_fps: Target frames per second
        """
        self.camera_index = camera_index
        self.target_fps = target_fps
        self.cap = None
        self.logger = get_logger()
        
        self._frame_count = 0
        self._dropped_frames = 0
        self._last_frame_time = 0
        self._frame_times = []
    
    def open(self) -> bool:
        """
        Open the camera.
        
        Returns:
            True if camera opened successfully
        """
        from ..runtime.dependency_check import safe_import_cv2
        cv2 = safe_import_cv2()
        
        if cv2 is None:
            self.logger.error("OpenCV not available")
            return False
        
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            
            if not self.cap.isOpened():
                self.logger.error(f"Failed to open camera {self.camera_index}")
                return False
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, self.target_fps)
            
            self.logger.info(f"Camera {self.camera_index} opened successfully")
            self._frame_count = 0
            self._dropped_frames = 0
            self._last_frame_time = time.time()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to open camera: {str(e)}")
            return False
    
    def read_frame(self) -> Optional[Tuple]:
        """
        Read a frame from the camera.
        
        Returns:
            Tuple of (success, frame, frame_rgb) or None if failed
        """
        if self.cap is None:
            return None
        
        from ..runtime.dependency_check import safe_import_cv2
        cv2 = safe_import_cv2()
        
        if cv2 is None:
            return None
        
        try:
            ret, frame = self.cap.read()
            
            if not ret:
                self._dropped_frames += 1
                return None
            
            # Convert BGR to RGB for MediaPipe
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Update timing
            current_time = time.time()
            frame_time = current_time - self._last_frame_time
            self._frame_times.append(frame_time)
            if len(self._frame_times) > 30:
                self._frame_times.pop(0)
            self._last_frame_time = current_time
            self._frame_count += 1
            
            return (True, frame, frame_rgb)
            
        except Exception as e:
            self.logger.error(f"Frame read error: {str(e)}")
            self._dropped_frames += 1
            return None
    
    def release(self):
        """Release the camera."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            self.logger.info("Camera released")
    
    def is_opened(self) -> bool:
        """Check if camera is currently opened."""
        return self.cap is not None and self.cap.isOpened()
    
    def get_frame_count(self) -> int:
        """Get total number of frames captured."""
        return self._frame_count
    
    def get_dropped_frames(self) -> int:
        """Get number of dropped frames."""
        return self._dropped_frames
    
    def get_average_fps(self) -> float:
        """Get average FPS over recent frames."""
        if not self._frame_times:
            return 0.0
        
        avg_frame_time = sum(self._frame_times) / len(self._frame_times)
        if avg_frame_time > 0:
            return 1.0 / avg_frame_time
        return 0.0
    
    def get_average_latency(self) -> float:
        """Get average frame latency in milliseconds."""
        if not self._frame_times:
            return 0.0
        
        avg_frame_time = sum(self._frame_times) / len(self._frame_times)
        return avg_frame_time * 1000.0
    
    def get_resolution(self) -> Tuple[int, int]:
        """Get camera resolution (width, height)."""
        from ..runtime.dependency_check import safe_import_cv2
        cv2 = safe_import_cv2()
        
        if self.cap is None or cv2 is None:
            return (0, 0)
        
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return (width, height)
