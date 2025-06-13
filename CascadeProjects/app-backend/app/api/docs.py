from fastapi import APIRouter, Depends
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from typing import Dict, Any

router = APIRouter()

def custom_openapi() -> Dict[str, Any]:
    """
    Custom OpenAPI documentation with enhanced descriptions and examples.
    """
    if router.app.openapi_schema:
        return router.app.openapi_schema

    openapi_schema = get_openapi(
        title="Opportunity AI API Documentation",
        version="1.0.0",
        description="API documentation for Opportunity AI job application system",
        routes=router.app.routes,
    )

    # Add custom tags
    openapi_schema["tags"] = [
        {
            "name": "application",
            "description": "Operations for submitting job applications"
        },
        {
            "name": "health",
            "description": "Health check endpoints"
        }
    ]

    # Add custom security schemes
    openapi_schema["components"] = {
        "securitySchemes": {
            "Bearer": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        }
    }

    # Add examples to endpoints
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["tags"] = ["application"]
            
            if method == "post":
                openapi_schema["paths"][path][method]["requestBody"]["content"]["multipart/form-data"]["schema"]["example"] = {
                    "fullName": "John Doe",
                    "userEmail": "john@example.com",
                    "companyEmail": "hiring@company.com",
                    "jobTitle": "Software Engineer",
                    "cvFile": "example.pdf"
                }

    router.app.openapi_schema = openapi_schema
    return openapi_schema

@router.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """
    Custom Swagger UI documentation page.
    """
    return get_swagger_ui_html(
        openapi_url="/docs.json",
        title="Opportunity AI API Documentation",
        swagger_favicon_url="/static/favicon.ico"
    )

@router.get("/redoc", include_in_schema=False)
async def custom_redoc_html():
    """
    Custom ReDoc documentation page.
    """
    return get_redoc_html(
        openapi_url="/docs.json",
        title="Opportunity AI API Documentation",
        redoc_favicon_url="/static/favicon.ico"
    )

@router.get("/docs.json", include_in_schema=False)
async def get_openapi_json():
    """
    Get OpenAPI JSON schema.
    """
    return custom_openapi()
