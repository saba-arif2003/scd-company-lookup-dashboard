from fastapi import APIRouter, Depends
from typing import Dict, Any
import time
import psutil
import asyncio
import aiohttp
from datetime import datetime, timedelta
import logging

from app.models.common import HealthCheck, APIResponse, APIStatus
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Track application start time
_start_time = time.time()


async def check_external_service(url: str, timeout: int = 5) -> str:
    """Check if an external service is accessible"""
    try:
        timeout_obj = aiohttp.ClientTimeout(total=timeout)
        async with aiohttp.ClientSession(timeout=timeout_obj) as session:
            async with session.get(url, headers={"User-Agent": settings.SEC_USER_AGENT}) as response:
                if response.status == 200:
                    return "healthy"
                else:
                    return f"unhealthy (status: {response.status})"
    except asyncio.TimeoutError:
        return "timeout"
    except aiohttp.ClientError as e:
        return f"error ({type(e).__name__})"
    except Exception as e:
        return f"unknown_error ({type(e).__name__})"


async def get_system_metrics() -> Dict[str, Any]:
    """Get system performance metrics"""
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_mb = memory.used / (1024 * 1024)
        memory_percent = memory.percent
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        
        return {
            "cpu_usage_percent": round(cpu_percent, 1),
            "memory_usage_mb": round(memory_mb, 1),
            "memory_usage_percent": round(memory_percent, 1),
            "disk_usage_percent": round(disk_percent, 1),
            "active_connections": len(psutil.net_connections())
        }
    except Exception as e:
        logger.warning(f"Failed to get system metrics: {str(e)}")
        return {"error": f"Failed to collect metrics: {str(e)}"}


@router.get("/health", response_model=APIResponse)
async def health_check():
    """
    Health check endpoint
    
    Returns the health status of the application and its dependencies.
    """
    start_time = time.time()
    
    try:
        # Calculate uptime
        uptime_seconds = time.time() - _start_time
        
        # Check external service dependencies
        dependencies_tasks = [
            check_external_service("https://data.sec.gov/api/xbrl/companyconcept/CIK0000320193/us-gaap/Assets.json"),
            check_external_service("https://query1.finance.yahoo.com/v8/finance/chart/AAPL")
        ]
        
        dependency_results = await asyncio.gather(*dependencies_tasks, return_exceptions=True)
        
        dependencies = {
            "sec_edgar_api": dependency_results[0] if not isinstance(dependency_results[0], Exception) else "error",
            "yahoo_finance": dependency_results[1] if not isinstance(dependency_results[1], Exception) else "error"
        }
        
        # Get system metrics
        system_metrics = await get_system_metrics()
        
        # Determine overall health status
        unhealthy_deps = [dep for status in dependencies.values() if not status.startswith("healthy")]
        
        if len(unhealthy_deps) == len(dependencies):
            overall_status = "unhealthy"
        elif unhealthy_deps:
            overall_status = "degraded"
        else:
            overall_status = "healthy"
        
        # Create health check response
        health_data = HealthCheck(
            status=overall_status,
            timestamp=datetime.utcnow(),
            version="1.0.0",
            uptime_seconds=round(uptime_seconds, 2),
            dependencies=dependencies,
            system_metrics=system_metrics,
            environment="development" if settings.DEBUG else "production"
        )
        
        # Determine API response status
        if overall_status == "healthy":
            api_status = APIStatus.SUCCESS
        elif overall_status == "degraded":
            api_status = APIStatus.WARNING
        else:
            api_status = APIStatus.ERROR
        
        response_time = round((time.time() - start_time) * 1000, 2)
        
        return APIResponse(
            status=api_status,
            message=f"Health check completed - {overall_status}",
            data=health_data.dict(),
            metadata={
                "response_time_ms": response_time,
                "checks_performed": len(dependencies) + 1  # +1 for system metrics
            }
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        
        # Return minimal health check on error
        health_data = HealthCheck(
            status="error",
            timestamp=datetime.utcnow(),
            version="1.0.0",
            uptime_seconds=round(time.time() - _start_time, 2),
            dependencies={
                "sec_edgar_api": "unknown",
                "yahoo_finance": "unknown"
            },
            environment="development" if settings.DEBUG else "production"
        )
        
        return APIResponse(
            status=APIStatus.ERROR,
            message=f"Health check failed: {str(e)}",
            data=health_data.dict(),
            metadata={
                "error": True,
                "response_time_ms": round((time.time() - start_time) * 1000, 2)
            }
        )


@router.get("/health/simple")
async def simple_health_check():
    """
    Simple health check endpoint for load balancers
    
    Returns a minimal response for basic health checking.
    """
    return {
        "status": "ok", 
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": round(time.time() - _start_time, 2)
    }


@router.get("/health/dependencies")
async def dependencies_health_check():
    """
    Check health of external dependencies only
    
    Returns the status of external services without system metrics.
    """
    try:
        # Check dependencies
        dependencies_tasks = [
            check_external_service("https://data.sec.gov/api/xbrl/companyconcept/CIK0000320193/us-gaap/Assets.json"),
            check_external_service("https://query1.finance.yahoo.com/v8/finance/chart/AAPL")
        ]
        
        dependency_results = await asyncio.gather(*dependencies_tasks, return_exceptions=True)
        
        dependencies = {
            "sec_edgar_api": {
                "status": dependency_results[0] if not isinstance(dependency_results[0], Exception) else "error",
                "url": "https://data.sec.gov",
                "description": "SEC EDGAR API for company filings"
            },
            "yahoo_finance": {
                "status": dependency_results[1] if not isinstance(dependency_results[1], Exception) else "error", 
                "url": "https://query1.finance.yahoo.com",
                "description": "Yahoo Finance API for stock prices"
            }
        }
        
        # Count healthy dependencies
        healthy_count = sum(1 for dep in dependencies.values() if dep["status"].startswith("healthy"))
        total_count = len(dependencies)
        
        return {
            "dependencies": dependencies,
            "summary": {
                "healthy": healthy_count,
                "total": total_count,
                "health_percentage": round((healthy_count / total_count) * 100, 1)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Dependencies health check failed: {str(e)}", exc_info=True)
        return {
            "error": f"Failed to check dependencies: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }