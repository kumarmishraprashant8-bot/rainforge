"""
API Documentation Configuration
OpenAPI/Swagger documentation with examples
"""

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def custom_openapi(app: FastAPI):
    """Generate custom OpenAPI schema with enhanced documentation."""
    
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="RainForge API",
        version="3.0.0",
        description="""
# RainForge - Rainwater Harvesting Platform API

Complete API for rainwater harvesting assessment, installation, monitoring, and management.

## Overview

RainForge provides a comprehensive platform for:
- **Assessments**: Calculate rainwater harvesting potential for any property
- **Projects**: Manage RWH installations from planning to completion
- **Monitoring**: Real-time tank levels and sensor data
- **Marketplace**: Connect with verified installers
- **Verification**: Photo-based installation verification
- **Payments**: Escrow-based milestone payments

## Authentication

Most endpoints require authentication via JWT tokens:

```
Authorization: Bearer <your_token>
```

Get tokens via `/api/v1/auth/login` or OAuth endpoints.

## Rate Limits

| Endpoint Type | Limit |
|---------------|-------|
| Public | 100 req/min |
| Authenticated | 500 req/min |
| Bulk operations | 10 req/min |

## Response Format

All responses follow this format:

```json
{
  "success": true,
  "data": { ... },
  "message": "Optional message",
  "errors": []
}
```

## WebSocket

Real-time updates available at `wss://api.rainforge.gov.in/ws`

## SDKs

- Python: `pip install rainforge`
- JavaScript: `npm install @rainforge/sdk`

## Support

- Email: api-support@rainforge.gov.in
- Docs: https://docs.rainforge.gov.in
        """,
        routes=app.routes,
        terms_of_service="https://rainforge.gov.in/terms",
        contact={
            "name": "RainForge API Support",
            "url": "https://rainforge.gov.in/support",
            "email": "api@rainforge.gov.in"
        },
        license_info={
            "name": "Government Open License",
            "url": "https://data.gov.in/license"
        }
    )
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT token"
        },
        "apiKey": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API key for service accounts"
        },
        "oauth2": {
            "type": "oauth2",
            "flows": {
                "authorizationCode": {
                    "authorizationUrl": "https://rainforge.gov.in/oauth/authorize",
                    "tokenUrl": "https://api.rainforge.gov.in/oauth/token",
                    "scopes": {
                        "read:projects": "Read project data",
                        "write:projects": "Create and modify projects",
                        "read:monitoring": "Access sensor data",
                        "admin": "Full administrative access"
                    }
                }
            }
        }
    }
    
    # Add tags with descriptions
    openapi_schema["tags"] = [
        {
            "name": "assessments",
            "description": "RWH potential assessment endpoints",
            "externalDocs": {
                "description": "Assessment Guide",
                "url": "https://docs.rainforge.gov.in/assessments"
            }
        },
        {
            "name": "projects",
            "description": "Project management endpoints"
        },
        {
            "name": "monitoring",
            "description": "Tank levels and sensor data"
        },
        {
            "name": "marketplace",
            "description": "Installer marketplace and bidding"
        },
        {
            "name": "payments",
            "description": "Payment processing and escrow"
        },
        {
            "name": "verification",
            "description": "Photo verification and compliance"
        },
        {
            "name": "authentication",
            "description": "User authentication and authorization"
        },
        {
            "name": "utilities",
            "description": "PDF, QR, export, and other utilities"
        },
        {
            "name": "advanced",
            "description": "Advanced features (forecasting, chatbot, etc.)"
        },
        {
            "name": "admin",
            "description": "Administrative endpoints",
            "x-requires-role": "admin"
        }
    ]
    
    # Add servers
    openapi_schema["servers"] = [
        {
            "url": "https://api.rainforge.gov.in",
            "description": "Production server"
        },
        {
            "url": "https://staging-api.rainforge.gov.in",
            "description": "Staging server"
        },
        {
            "url": "http://localhost:8000",
            "description": "Local development"
        }
    ]
    
    # Add common response schemas
    openapi_schema["components"]["schemas"]["ErrorResponse"] = {
        "type": "object",
        "properties": {
            "success": {"type": "boolean", "example": False},
            "error": {"type": "string", "example": "Resource not found"},
            "code": {"type": "string", "example": "NOT_FOUND"},
            "details": {"type": "object", "additionalProperties": True}
        }
    }
    
    openapi_schema["components"]["schemas"]["PaginatedResponse"] = {
        "type": "object",
        "properties": {
            "items": {"type": "array", "items": {}},
            "total": {"type": "integer", "example": 100},
            "page": {"type": "integer", "example": 1},
            "per_page": {"type": "integer", "example": 20},
            "pages": {"type": "integer", "example": 5}
        }
    }
    
    # Add examples
    openapi_schema["components"]["examples"] = {
        "AssessmentRequest": {
            "summary": "Standard assessment request",
            "value": {
                "roof_area_sqm": 150,
                "city": "Mumbai",
                "state": "Maharashtra",
                "latitude": 19.0760,
                "longitude": 72.8777,
                "roof_type": "rcc",
                "existing_system": False
            }
        },
        "AssessmentResponse": {
            "summary": "Standard assessment response",
            "value": {
                "annual_rainfall_mm": 2400,
                "annual_collection_liters": 288000,
                "recommended_tank_liters": 10000,
                "roi_years": 3.5,
                "carbon_offset_kg": 144,
                "water_cost_savings_inr": 28800,
                "rpi_score": 85
            }
        },
        "ProjectCreate": {
            "summary": "Create project",
            "value": {
                "name": "Sharma Residence RWH",
                "address": "123 Green Lane, Andheri West",
                "city": "Mumbai",
                "state": "Maharashtra",
                "roof_area_sqm": 150,
                "tank_capacity_liters": 10000
            }
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


def setup_api_documentation(app: FastAPI):
    """Configure API documentation for the application."""
    
    # Use custom OpenAPI generator
    app.openapi = lambda: custom_openapi(app)
    
    # Configure Swagger UI settings
    app.swagger_ui_parameters = {
        "deepLinking": True,
        "displayRequestDuration": True,
        "docExpansion": "list",
        "operationsSorter": "alpha",
        "filter": True,
        "tagsSorter": "alpha",
        "syntaxHighlight.theme": "monokai",
        "tryItOutEnabled": True,
        "persistAuthorization": True
    }
    
    return app


# API response models for documentation
from pydantic import BaseModel, Field
from typing import Optional, List, Any


class APIResponse(BaseModel):
    """Standard API response wrapper."""
    success: bool = Field(True, description="Whether the request was successful")
    data: Optional[Any] = Field(None, description="Response payload")
    message: Optional[str] = Field(None, description="Optional message")
    errors: List[str] = Field(default_factory=list, description="List of errors if any")


class PaginationParams(BaseModel):
    """Pagination query parameters."""
    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    per_page: int = Field(20, ge=1, le=100, description="Items per page")
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="Sort order")


class FilterParams(BaseModel):
    """Common filter parameters."""
    status: Optional[str] = Field(None, description="Filter by status")
    created_after: Optional[str] = Field(None, description="Filter by creation date (ISO format)")
    created_before: Optional[str] = Field(None, description="Filter by creation date (ISO format)")
    search: Optional[str] = Field(None, description="Search query")


# Health check responses
class HealthCheck(BaseModel):
    """Health check response."""
    status: str = Field(..., example="healthy")
    version: str = Field(..., example="3.0.0")
    uptime: str = Field(..., example="5d 12h 30m")
    timestamp: str = Field(..., example="2024-01-15T12:00:00Z")


class DetailedHealthCheck(HealthCheck):
    """Detailed health check with component status."""
    components: dict = Field(
        ...,
        example={
            "database": {"status": "healthy", "latency_ms": 5},
            "redis": {"status": "healthy", "latency_ms": 2},
            "mqtt": {"status": "healthy", "connections": 15}
        }
    )
