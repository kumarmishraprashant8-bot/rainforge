"""
System Health Dashboard Service
Monitor backend health, performance, and resource usage
"""
import os
import time
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from dataclasses import dataclass


@dataclass
class HealthCheck:
    """Health check result."""
    name: str
    status: str  # healthy, degraded, unhealthy
    latency_ms: float
    message: Optional[str] = None
    last_check: str = None


@dataclass
class SystemMetrics:
    """System metrics."""
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    uptime_seconds: float
    request_count: int
    error_rate: float


class HealthDashboardService:
    """
    Monitor system health and performance.
    
    Monitors:
    - Database connectivity
    - Cache (Redis) status
    - External API health
    - System resources
    - Request metrics
    """
    
    def __init__(self):
        self._start_time = time.time()
        self._request_count = 0
        self._error_count = 0
        self._health_cache: Dict[str, HealthCheck] = {}
        self._metrics_history: List[Dict] = []
    
    async def get_health_summary(self) -> Dict[str, Any]:
        """Get overall health summary."""
        checks = await self.run_all_health_checks()
        
        # Determine overall status
        statuses = [c.status for c in checks]
        if all(s == "healthy" for s in statuses):
            overall = "healthy"
        elif any(s == "unhealthy" for s in statuses):
            overall = "unhealthy"
        else:
            overall = "degraded"
        
        return {
            "status": overall,
            "timestamp": datetime.utcnow().isoformat(),
            "uptime": self._format_uptime(time.time() - self._start_time),
            "checks": [
                {
                    "name": c.name,
                    "status": c.status,
                    "latency_ms": c.latency_ms,
                    "message": c.message
                }
                for c in checks
            ],
            "metrics": await self.get_system_metrics()
        }
    
    async def run_all_health_checks(self) -> List[HealthCheck]:
        """Run all health checks."""
        checks = await asyncio.gather(
            self.check_database(),
            self.check_redis(),
            self.check_mqtt(),
            self.check_disk(),
            self.check_memory(),
            return_exceptions=True
        )
        
        results = []
        for check in checks:
            if isinstance(check, Exception):
                results.append(HealthCheck(
                    name="unknown",
                    status="unhealthy",
                    latency_ms=0,
                    message=str(check)
                ))
            else:
                results.append(check)
        
        return results
    
    async def check_database(self) -> HealthCheck:
        """Check database connectivity."""
        start = time.time()
        
        try:
            # Simulate database check (would actually query DB)
            await asyncio.sleep(0.01)
            
            latency = (time.time() - start) * 1000
            
            return HealthCheck(
                name="database",
                status="healthy" if latency < 100 else "degraded",
                latency_ms=round(latency, 2),
                message="PostgreSQL connection OK",
                last_check=datetime.utcnow().isoformat()
            )
        except Exception as e:
            return HealthCheck(
                name="database",
                status="unhealthy",
                latency_ms=(time.time() - start) * 1000,
                message=str(e)
            )
    
    async def check_redis(self) -> HealthCheck:
        """Check Redis connectivity."""
        start = time.time()
        
        try:
            # Simulate Redis ping
            await asyncio.sleep(0.005)
            
            latency = (time.time() - start) * 1000
            
            return HealthCheck(
                name="redis",
                status="healthy" if latency < 50 else "degraded",
                latency_ms=round(latency, 2),
                message="Redis connection OK",
                last_check=datetime.utcnow().isoformat()
            )
        except Exception as e:
            return HealthCheck(
                name="redis",
                status="unhealthy" if "connection" in str(e).lower() else "degraded",
                latency_ms=(time.time() - start) * 1000,
                message=str(e)
            )
    
    async def check_mqtt(self) -> HealthCheck:
        """Check MQTT broker connectivity."""
        start = time.time()
        
        try:
            # Simulate MQTT check
            await asyncio.sleep(0.02)
            
            latency = (time.time() - start) * 1000
            
            return HealthCheck(
                name="mqtt_broker",
                status="healthy",
                latency_ms=round(latency, 2),
                message="MQTT broker reachable",
                last_check=datetime.utcnow().isoformat()
            )
        except Exception as e:
            return HealthCheck(
                name="mqtt_broker",
                status="degraded",
                latency_ms=(time.time() - start) * 1000,
                message=str(e)
            )
    
    async def check_disk(self) -> HealthCheck:
        """Check disk space."""
        try:
            # Get disk usage (cross-platform)
            import shutil
            total, used, free = shutil.disk_usage("/")
            
            percent_used = (used / total) * 100
            free_gb = free / (1024**3)
            
            if percent_used > 90:
                status = "unhealthy"
                message = f"Critical: Only {free_gb:.1f}GB free"
            elif percent_used > 80:
                status = "degraded"
                message = f"Warning: {free_gb:.1f}GB free"
            else:
                status = "healthy"
                message = f"OK: {free_gb:.1f}GB free ({100-percent_used:.1f}%)"
            
            return HealthCheck(
                name="disk",
                status=status,
                latency_ms=0,
                message=message,
                last_check=datetime.utcnow().isoformat()
            )
        except Exception as e:
            return HealthCheck(
                name="disk",
                status="degraded",
                latency_ms=0,
                message=str(e)
            )
    
    async def check_memory(self) -> HealthCheck:
        """Check memory usage."""
        try:
            import psutil
            memory = psutil.virtual_memory()
            
            if memory.percent > 90:
                status = "unhealthy"
            elif memory.percent > 80:
                status = "degraded"
            else:
                status = "healthy"
            
            return HealthCheck(
                name="memory",
                status=status,
                latency_ms=0,
                message=f"{memory.percent:.1f}% used ({memory.available/1024**3:.1f}GB available)",
                last_check=datetime.utcnow().isoformat()
            )
        except ImportError:
            return HealthCheck(
                name="memory",
                status="degraded",
                latency_ms=0,
                message="psutil not available"
            )
        except Exception as e:
            return HealthCheck(
                name="memory",
                status="degraded",
                latency_ms=0,
                message=str(e)
            )
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        try:
            import psutil
            
            cpu = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            
            return {
                "cpu_percent": cpu,
                "memory_percent": memory.percent,
                "memory_used_gb": memory.used / 1024**3,
                "memory_total_gb": memory.total / 1024**3,
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / 1024**3,
                "uptime_seconds": time.time() - self._start_time,
                "request_count": self._request_count,
                "error_rate": self._error_count / max(self._request_count, 1) * 100,
                "python_version": os.sys.version.split()[0]
            }
        except ImportError:
            return {
                "cpu_percent": 0,
                "memory_percent": 0,
                "uptime_seconds": time.time() - self._start_time,
                "request_count": self._request_count,
                "error_rate": 0,
                "message": "psutil not available for detailed metrics"
            }
    
    async def get_request_metrics(
        self,
        period: str = "hour"
    ) -> Dict[str, Any]:
        """Get request metrics for period."""
        # Mock data - would come from actual metrics in production
        import random
        
        if period == "hour":
            points = 60
            labels = [f"{i}m" for i in range(60)]
        elif period == "day":
            points = 24
            labels = [f"{i}h" for i in range(24)]
        else:
            points = 30
            labels = [f"Day {i+1}" for i in range(30)]
        
        return {
            "period": period,
            "labels": labels,
            "requests": [random.randint(50, 200) for _ in range(points)],
            "errors": [random.randint(0, 5) for _ in range(points)],
            "latency_p50": [random.uniform(20, 50) for _ in range(points)],
            "latency_p99": [random.uniform(100, 300) for _ in range(points)]
        }
    
    async def get_endpoint_stats(self) -> List[Dict]:
        """Get per-endpoint statistics."""
        # Mock data
        return [
            {"endpoint": "/api/v1/assessments", "method": "GET", "calls": 1250, "avg_ms": 45, "errors": 2},
            {"endpoint": "/api/v1/assessments", "method": "POST", "calls": 340, "avg_ms": 120, "errors": 5},
            {"endpoint": "/api/v1/projects", "method": "GET", "calls": 890, "avg_ms": 35, "errors": 1},
            {"endpoint": "/api/v1/verify/photo", "method": "POST", "calls": 560, "avg_ms": 450, "errors": 12},
            {"endpoint": "/api/v1/payments/webhook", "method": "POST", "calls": 230, "avg_ms": 85, "errors": 3},
            {"endpoint": "/api/v1/monitoring/telemetry", "method": "POST", "calls": 15600, "avg_ms": 15, "errors": 8}
        ]
    
    def record_request(self, success: bool = True, latency_ms: float = 0):
        """Record request for metrics."""
        self._request_count += 1
        if not success:
            self._error_count += 1
    
    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human-readable format."""
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"


# Singleton
_health_service: Optional[HealthDashboardService] = None

def get_health_service() -> HealthDashboardService:
    global _health_service
    if _health_service is None:
        _health_service = HealthDashboardService()
    return _health_service
