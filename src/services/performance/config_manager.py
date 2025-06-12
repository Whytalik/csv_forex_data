import psutil  # type: ignore


class ConfigManager:
    """Manage configuration settings for optimal performance."""

    @staticmethod
    def get_optimal_concurrency() -> int:
        """Get optimal concurrency based on system resources"""
        cpu_count = psutil.cpu_count()
        memory_gb = psutil.virtual_memory().total / (1024**3)

        # Conservative approach for forex data processing
        if memory_gb > 16:
            return min(8, cpu_count)
        elif memory_gb > 8:
            return min(5, cpu_count)
        else:
            return min(3, cpu_count)

    @staticmethod
    def get_chunk_size(file_size_mb: float) -> int:
        """Get optimal chunk size for processing based on file size"""
        if file_size_mb > 100:
            return 10000
        elif file_size_mb > 50:
            return 5000
        else:
            return 1000

    @staticmethod
    def get_memory_usage_mb() -> float:
        """Get current memory usage in MB"""
        return psutil.virtual_memory().used / (1024**2)

    @staticmethod
    def get_available_memory_gb() -> float:
        """Get available memory in GB"""
        return psutil.virtual_memory().available / (1024**3)

    @staticmethod
    def should_use_cache(file_size_mb: float) -> bool:
        """Determine if caching should be used based on file size and available memory"""
        available_gb = ConfigManager.get_available_memory_gb()
        return file_size_mb < 50 and available_gb > 2.0
