"""
RainForge Celery Application
============================
Async task queue for bulk processing, PDF generation, and ML inference.

Owners: Prashant Mishra & Ishita Parmar
"""

import os
from celery import Celery
from celery.schedules import crontab

# Redis URL from environment or default
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "rainforge",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "app.worker.tasks.bulk_processor",
        "app.worker.tasks.pdf_generator",
        "app.worker.tasks.ml_inference",
        "app.worker.tasks.geocoder",
    ]
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    
    # Worker settings
    worker_prefetch_multiplier=1,
    worker_concurrency=4,
    
    # Task execution limits
    task_soft_time_limit=300,  # 5 minutes
    task_time_limit=600,  # 10 minutes hard limit
    
    # Result backend settings
    result_expires=3600,  # 1 hour
    
    # Rate limiting
    task_annotations={
        "app.worker.tasks.geocoder.*": {"rate_limit": "10/m"},  # Geocoding rate limit
        "app.worker.tasks.ml_inference.*": {"rate_limit": "30/m"},  # ML rate limit
    },
    
    # Retry settings
    task_default_retry_delay=30,
    task_max_retries=3,
)

# Periodic tasks (beat schedule)
celery_app.conf.beat_schedule = {
    # Clean up old jobs every hour
    "cleanup-old-jobs": {
        "task": "app.worker.tasks.bulk_processor.cleanup_old_jobs",
        "schedule": crontab(minute=0),  # Every hour
    },
    # Generate daily analytics report
    "daily-analytics": {
        "task": "app.worker.tasks.analytics.generate_daily_report",
        "schedule": crontab(hour=6, minute=0),  # 6 AM daily
    },
    # Sync weather data
    "sync-weather": {
        "task": "app.worker.tasks.weather_sync.fetch_forecasts",
        "schedule": crontab(hour="*/6"),  # Every 6 hours
    },
}


# Task routing
celery_app.conf.task_routes = {
    "app.worker.tasks.bulk_processor.*": {"queue": "bulk"},
    "app.worker.tasks.pdf_generator.*": {"queue": "pdf"},
    "app.worker.tasks.ml_inference.*": {"queue": "ml"},
    "app.worker.tasks.geocoder.*": {"queue": "geocode"},
}


if __name__ == "__main__":
    celery_app.start()
