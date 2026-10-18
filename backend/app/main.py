from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError

import app.entities  # noqa: F401  (registra as tabelas no Base antes do create_all)
from app.config import BASE_DIR
from app.controllers import autenticacao_controller, locacao_controller, usuario_controller, veiculo_controller
from app.database import Base, engine
from app.exceptions import NegocioException


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


# docs_url=None: o /docs padrão baixa o Swagger da internet; o nosso (abaixo) usa os arquivos de backend/static
app = FastAPI(title="OCar API", lifespan=lifespan, docs_url=None, redoc_url=None)

# O front-end roda em outra porta (servidor.py), então liberamos CORS
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/docs", include_in_schema=False)
async def swagger() -> HTMLResponse:
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="OCar API - Swagger",
        swagger_js_url="/static/swagger-ui/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui/swagger-ui.css",
        swagger_favicon_url="/static/swagger-ui/favicon-32x32.png",
    )


@app.exception_handler(NegocioException)
async def tratar_negocio_exception(_: Request, exc: NegocioException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.mensagem})


# Última barreira: se duas requisições cadastrarem o mesmo login/placa ao mesmo tempo,
# a checagem do service passa nas duas e o UNIQUE do banco barra a segunda
@app.exception_handler(IntegrityError)
async def tratar_integrity_error(_: Request, exc: IntegrityError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": "Registro duplicado ou inválido"})


app.include_router(autenticacao_controller.router)
app.include_router(usuario_controller.router)
app.include_router(veiculo_controller.router)
app.include_router(locacao_controller.router)
