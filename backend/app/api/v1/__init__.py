"""API v1 router."""
from fastapi import APIRouter

from app.api.v1 import users, income, expenses, uc, tax, export, billing, web, auth

api_router = APIRouter()

api_router.include_router(users.router)
api_router.include_router(income.router)
api_router.include_router(expenses.router)
api_router.include_router(uc.router)
api_router.include_router(tax.router)
api_router.include_router(export.router)
api_router.include_router(billing.router)

# Web UI routes (no /api/v1 prefix)
web_router = APIRouter()
web_router.include_router(auth.router)
web_router.include_router(web.router)
