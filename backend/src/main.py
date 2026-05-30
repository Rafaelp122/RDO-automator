from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.config import Settings, settings
from src.exceptions import AppError
from src.routes import router
from src.schemas import ErrorResponse


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: blob:"
        )
        return response


def create_app(app_settings: Settings | None = None) -> FastAPI:
    """Factory que cria e configura a aplicação FastAPI.

    Recebe opcionalmente um objeto ``Settings`` para injeção de
    configuração em testes ou ambientes alternativos.
    """
    if app_settings is None:
        app_settings = settings

    app = FastAPI(title="RDO Automator API", version="2.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(SecurityHeadersMiddleware)

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(detail=exc.detail, code=exc.code, errors=[]).model_dump(),
        )

    @app.middleware("http")
    async def max_upload_size_middleware(request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > app_settings.max_upload_bytes:
            return JSONResponse(
                status_code=413,
                content=ErrorResponse(
                    detail=f"Payload excede o limite de {app_settings.max_upload_mb} MB",
                    code="payload_too_large",
                ).model_dump(),
            )
        return await call_next(request)

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    app.include_router(router)

    return app


app = create_app()
