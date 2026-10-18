from datetime import datetime, timedelta, timezone

import jwt
import pytest
from sqlalchemy import text

from app.config import JWT_ALGORITHM, SECRET_KEY
from app.database import engine


def token(payload: dict, chave: str = SECRET_KEY, algoritmo: str = JWT_ALGORITHM) -> str:
    return jwt.encode(payload, chave, algorithm=algoritmo)


def futuro() -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=1)


@pytest.mark.parametrize(
    "authorization",
    [
        None,
        "",
        "Bearer",
        "Bearer ",
        "Bearer lixo",
        "Bearer a.b.c",
        "Basic dXNlcjpzZW5oYQ==",
    ],
)
def test_token_ausente_ou_malformado(client, cliente, authorization):
    headers = {} if authorization is None else {"Authorization": authorization}
    r = client.get("/usuarios/meus-dados", headers=headers)
    assert r.status_code == 401
    assert isinstance(r.json()["detail"], str)


def test_esquema_diferente_de_bearer_com_token_valido(client, cliente):
    valido = cliente.headers["Authorization"].removeprefix("Bearer ")
    assert client.get("/usuarios/meus-dados", headers={"Authorization": f"Token {valido}"}).status_code == 401


def test_bearer_em_minusculo_e_aceito(client, cliente):
    valido = cliente.headers["Authorization"].removeprefix("Bearer ")
    assert client.get("/usuarios/meus-dados", headers={"Authorization": f"bearer {valido}"}).status_code == 200


@pytest.mark.parametrize(
    "gerar",
    [
        pytest.param(lambda id: token({"sub": str(id), "exp": datetime.now(timezone.utc) - timedelta(seconds=1)}), id="expirado"),
        pytest.param(lambda id: token({"sub": str(id), "exp": futuro()}, chave="outra-chave-qualquer-com-32-bytes!!"), id="chave-errada"),
        pytest.param(lambda id: token({"sub": str(id), "exp": futuro()}, chave=None, algoritmo="none"), id="alg-none"),
        pytest.param(lambda id: token({"sub": "abc", "exp": futuro()}), id="sub-nao-numerico"),
        pytest.param(lambda id: token({"exp": futuro()}), id="sem-sub"),
        pytest.param(lambda id: token({"sub": "999", "exp": futuro()}), id="usuario-inexistente"),
    ],
)
def test_token_invalido(client, cliente, gerar):
    r = client.get("/usuarios/meus-dados", headers={"Authorization": f"Bearer {gerar(cliente.id)}"})
    assert r.status_code == 401
    assert r.json() == {"detail": "Token inválido ou expirado"}


def test_token_de_usuario_apagado_do_banco(client, cliente):
    # simula o banco recriado com o navegador ainda guardando o token antigo
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM usuario"))
    assert client.get("/usuarios/meus-dados", headers=cliente.headers).status_code == 401


def test_perfil_vem_do_banco_e_nao_do_token(client, cliente):
    # mesmo um token assinado dizendo FUNCIONARIO não dá acesso a quem é CLIENTE no banco
    forjado = token({"sub": str(cliente.id), "perfil": "FUNCIONARIO", "exp": futuro()})
    assert client.get("/veiculos", headers={"Authorization": f"Bearer {forjado}"}).status_code == 403


def test_token_de_outro_usuario_ve_os_dados_dele(client, cliente, funcionario):
    assert client.get("/usuarios/meus-dados", headers=funcionario.headers).json()["login"] == "jose"
    assert client.get("/usuarios/meus-dados", headers=cliente.headers).json()["login"] == "maria"


def test_cors_preflight_do_front(client):
    r = client.options(
        "/veiculos",
        headers={
            "Origin": "http://localhost:5500",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )
    assert r.status_code == 200
    assert r.headers["access-control-allow-origin"] in ("*", "http://localhost:5500")
    assert "authorization" in r.headers["access-control-allow-headers"].lower()


def test_cors_nas_respostas(client, cliente):
    r = client.get("/usuarios/meus-dados", headers={**cliente.headers, "Origin": "http://localhost:5500"})
    assert r.headers["access-control-allow-origin"] in ("*", "http://localhost:5500")


def test_rota_inexistente(client):
    assert client.get("/nao-existe").status_code == 404
