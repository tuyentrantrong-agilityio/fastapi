from fastapi import FastAPI


# METADATA - API Information
# ===========================
# Metadata is displayed in /docs (Swagger) and /redoc
# Specifically: title, description, version, contact info, license, etc.


# EXAMPLE 1: Basic metadata
# ========================

description = """
ChimichangApp API helps you do awesome stuff. 🚀

## Items

You can **read items**.

## Users

You will be able to:

* **Create users** (_not implemented_).
* **Read users** (_not implemented_).
"""

app = FastAPI(
    title="ChimichangApp",
    description=description,
    summary="Deadpool's favorite app. Nuff said.",
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Deadpoolio the Amazing",
        "url": "http://x-force.example.com/contact/",
        "email": "dp@x-force.example.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)


@app.get("/items/")
async def read_items():
    return [{"name": "Katana"}]


# EXAMPLE 2: License identifier (when using OpenAPI 3.1.0+)
# ======================================================
# Instead of "url", use "identifier" for standard licenses

app2 = FastAPI(
    title="ChimichangApp 2",
    description="Version 2 with identifier",
    version="0.0.2",
    license_info={
        "name": "Apache 2.0",
        "identifier": "Apache-2.0",  # Or: MIT, GPL, BSD-3-Clause...
    },
)


# EXAMPLE 3: Tags metadata - Group endpoints
# ============================================
# Tags help organize endpoints in /docs

tags_metadata = [
    {
        "name": "users",
        "description": "Operations with users. The **login** logic is also here.",
    },
    {
        "name": "items",
        "description": "Manage items. So _fancy_ they have their own docs.",
        "externalDocs": {
            "description": "Items external docs",
            "url": "https://fastapi.tiangolo.com/",
        },
    },
]

app3 = FastAPI(openapi_tags=tags_metadata)


@app3.get("/users/", tags=["users"])
async def get_users():
    return [{"name": "Harry"}, {"name": "Ron"}]


@app3.get("/items/", tags=["items"])
async def get_items():
    return [{"name": "wand"}, {"name": "flying broom"}]


# EXAMPLE 4: Custom docs URLs
# ============================
# Default: /docs (Swagger), /redoc
# You can change or disable them

# Change Swagger to /documentation, disable ReDoc
app4 = FastAPI(
    title="MyApp",
    docs_url="/documentation",
    redoc_url=None,
)


# EXAMPLE 5: Custom OpenAPI URL
# ==============================
# Default: /openapi.json
# Set to /api/v1/openapi.json instead

app5 = FastAPI(
    title="MyApp",
    openapi_url="/api/v1/openapi.json",
)


# EXAMPLE 6: Disable docs completely
# ====================================

app6 = FastAPI(
    title="Production App",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


# IMPORTANT
# ==========
# 1. title: API name, shown at top of docs
# 2. summary: Short description (OpenAPI 3.1.0+, FastAPI 0.99.0+)
# 3. description: Detailed description, supports Markdown
# 4. version: App version (not OpenAPI version)
# 5. terms_of_service: URL to terms
# 6. contact: Dict with name, url, email
# 7. license_info: Dict with name + (url or identifier)
# 8. openapi_tags: List of dicts for tags metadata
# 9. docs_url: URL for Swagger UI (default: /docs)
# 10. redoc_url: URL for ReDoc (default: /redoc)
# 11. openapi_url: URL for OpenAPI JSON (default: /openapi.json)
