from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import UserRole
from app.repositories import user_repo
from app.schemas.common import ErrorDetail, ErrorResponse


@asynccontextmanager
async def lifespan(_: FastAPI):
    import app.models  # noqa: F401 — register ORM mappers

    Base.metadata.create_all(bind=engine)
    settings = get_settings()
    if settings.admin_seed_email and settings.admin_seed_password:
        db = SessionLocal()
        try:
            if user_repo.count_users(db) == 0:
                user_repo.create(
                    db,
                    email=settings.admin_seed_email,
                    full_name="Administrator",
                    password=settings.admin_seed_password,
                    role=UserRole.admin,
                )
        finally:
            db.close()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        lifespan=lifespan,
    )

    if settings.cors_origins == "*":
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    else:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,  # type: ignore[arg-type]
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        _request: Request, exc: HTTPException
    ) -> JSONResponse:
        body = {"detail": exc.detail}
        if isinstance(exc.detail, dict) and "errors" in exc.detail:
            body = exc.detail
        return JSONResponse(status_code=exc.status_code, content=body)

    @app.exception_handler(RequestValidationError)
    async def validation_handler(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errs: list[ErrorDetail] = []
        for e in exc.errors():
            loc = e.get("loc", ())
            field = str(loc[-1]) if loc else None
            errs.append(ErrorDetail(field=field, message=str(e.get("msg", "invalid"))))
        r = ErrorResponse(
            detail="Validation error", errors=errs
        )
        return JSONResponse(
            status_code=422,
            content=r.model_dump(),
        )

    app.include_router(api_router, prefix="/api/v1")

    static_dir = Path(__file__).resolve().parent.parent / "static"
    if static_dir.is_dir():
        app.mount(
            "/static", StaticFiles(directory=str(static_dir)), name="static"
        )

        @app.get("/")
        async def root_index() -> FileResponse:
            return FileResponse(static_dir / "index.html")

        @app.get("/app")
        async def app_page() -> FileResponse:
            return FileResponse(static_dir / "app.html")

    return app


app = create_app()
