# import logging
# from urllib.parse import urlsplit

# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

# from app.config import get_settings
# from app.database import Base, engine
# from app.routers import copilot, complaints
# from app.models import complaint  # noqa: F401 -- ensures model is registered before create_all

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger("aivoa.startup")
# settings = get_settings()

# app = FastAPI(
#     title="AIVOA Customer Complaint Management API",
#     description="AI-powered pharmaceutical customer complaint intake, triage, and QMS logging.",
#     version="1.0.0",
# )

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=settings.cors_origin_list,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# app.include_router(copilot.router)
# app.include_router(complaints.router)


# @app.on_event("startup")
# def on_startup():
#     db_url = settings.sqlalchemy_database_url
#     parts = urlsplit(db_url)
#     safe_host = f"{parts.scheme}://{parts.hostname}:{parts.port or ''}{parts.path}"
#     logger.info("Connecting to database at: %s", safe_host)
#     if parts.hostname in ("localhost", "127.0.0.1", "::1"):
#         logger.warning(
#             "DATABASE_URL points at 'localhost' -- this only works for local dev. "
#             "On Render, set DATABASE_URL to your Postgres instance's Internal Database URL "
#             "(dashboard -> your Postgres -> Internal Database URL), not the .env.example placeholder."
#         )
#     Base.metadata.create_all(bind=engine)


# @app.get("/api/health")
# def health():
#     return {"status": "ok", "groq_enabled": settings.groq_enabled}



import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, engine
from app.routers import copilot, complaints
from app.models import complaint  # noqa: F401 -- ensures model is registered before create_all

logging.basicConfig(level=logging.INFO)
settings = get_settings()

app = FastAPI(
    title="AIVOA Customer Complaint Management API",
    description="AI-powered pharmaceutical customer complaint intake, triage, and QMS logging.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(copilot.router)
app.include_router(complaints.router)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/api/health")
def health():
    return {"status": "ok", "groq_enabled": settings.groq_enabled}
