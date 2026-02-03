from fastapi import APIRouter
from app.llm.api import router as llm_router
from app.nest.api.projects import router as nest_projects_router

# Backstage routers
from app.backstage.api.auth import router as auth_router
from app.backstage.api.dashboard import router as dashboard_router
from app.backstage.api.blogs import router as blogs_router
from app.backstage.api.snippets import router as snippets_router
from app.backstage.api.taxonomy import router as taxonomy_router
from app.backstage.api.common import router as common_router

api_router = APIRouter()

# Shared / Feature specific routes
api_router.include_router(llm_router, prefix="/ai", tags=["ai"])

# DevinNest Web Client Routes
# Prefix: /nest
nest_router = APIRouter()
nest_router.include_router(nest_projects_router, prefix="/projects", tags=["nest-projects"])
api_router.include_router(nest_router, prefix="/nest")

# DevinNest Backstage (Admin) Routes
# Prefix: /backstage
backstage_router = APIRouter()
backstage_router.include_router(auth_router, prefix="/auth", tags=["backstage-auth"])
backstage_router.include_router(dashboard_router, prefix="/dashboard", tags=["backstage-dashboard"])
backstage_router.include_router(blogs_router, prefix="/blogs", tags=["backstage-blogs"])
backstage_router.include_router(snippets_router, prefix="/snippets", tags=["backstage-snippets"])
backstage_router.include_router(taxonomy_router, tags=["backstage-taxonomy"]) # /categories, /tags are root relative
backstage_router.include_router(common_router, tags=["backstage-common"]) # /upload

api_router.include_router(backstage_router, prefix="/backstage")
