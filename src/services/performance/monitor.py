import time
import psutil  # type: ignore
from typing import Dict, Any


class PerformanceMonitor:
    """Monitor system performance during operations."""

    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.cpu_usage = []
        self.memory_usage = []

    def start_monitoring(self):
        """Start performance monitoring"""
        self.start_time = time.time()

    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.end_time = time.time()

    def get_current_stats(self) -> Dict[str, float]:
        """Get current system stats"""
        return {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_used_gb": psutil.virtual_memory().used / (1024**3),
        }

    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            current_stats = self.get_current_stats()

            return {
                "duration_seconds": round(duration, 2),
                "duration_minutes": round(duration / 60, 2),
                **current_stats,
            }
        return {}


# Global instance
performance_monitor = PerformanceMonitor()
