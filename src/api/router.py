from fastapi import APIRouter
from src.api.v1 import analytics, auth, chat, classify, compare, documents, search, summarize

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(documents.router)
api_router.include_router(search.router)
api_router.include_router(chat.router)
api_router.include_router(compare.router)
api_router.include_router(summarize.router)
api_router.include_router(classify.router)
api_router.include_router(analytics.router)
