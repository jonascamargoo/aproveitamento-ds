"""Tabela "Configurações de Acesso" do enunciado: cada endpoint com sem token, CLIENTE e FUNCIONARIO."""

import pytest
from dados import corpo_locacao, corpo_usuario, corpo_veiculo
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app

PUBLICO, AMBOS, FUNCIONARIO = "publico", "ambos", "funcionario"

ENDPOINTS = [
    ("POST", "/usuarios", corpo_usuario(login="novo"), PUBLICO),
    ("GET", "/usuarios/existe?login=maria", None, PUBLICO),
    ("POST", "/login", {"login": "maria", "senha": "123"}, PUBLICO),
    ("GET", "/usuarios/meus-dados", None, AMBOS),
    ("PATCH", "/usuarios/senha", {"senha": "123"}, AMBOS),
    ("GET", "/usuarios/clientes", None, FUNCIONARIO),
    ("GET", "/veiculos", None, FUNCIONARIO),
    ("GET", "/veiculos/1", None, AMBOS),
    ("GET", "/veiculos/existe?placa=ABC1D23", None, FUNCIONARIO),
    ("POST", "/veiculos", corpo_veiculo(placa="NOV0A00"), FUNCIONARIO),
    ("PATCH", "/veiculos/1", {"descricao": "Alterado"}, FUNCIONARIO),
    ("DELETE", "/veiculos/2", None, FUNCIONARIO),
    ("POST", "/locacoes", corpo_locacao(3, 1), FUNCIONARIO),
    ("GET", "/locacoes/minhas", None, AMBOS),
    ("GET", "/locacoes/1", None, AMBOS),
    ("PATCH", "/locacoes/1/finalizar", None, FUNCIONARIO),
]


@pytest.fixture(scope="module")
def cenario():
    """cliente id 1, funcionário id 2, veículos 1 (locado), 2 e 3 (livres), locação 1."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as client:
        for login, perfil in [("maria", "CLIENTE"), ("jose", "FUNCIONARIO")]:
            client.post("/usuarios", json=corpo_usuario(login=login, perfil=perfil))
        tokens = {
            login: {"Authorization": "Bearer " + client.post("/login", json={"login": login, "senha": "123"}).json()["token"]}
            for login in ("maria", "jose")
        }
        for placa in ("ABC1D23", "DEF4G56", "GHI7J89"):
            client.post("/veiculos", json=corpo_veiculo(placa=placa), headers=tokens["jose"])
        client.post("/locacoes", json=corpo_locacao(1, 1), headers=tokens["jose"])
        yield client, {"sem token": {}, "cliente": tokens["maria"], "funcionario": tokens["jose"]}


@pytest.mark.parametrize("quem", ["sem token", "cliente", "funcionario"])
@pytest.mark.parametrize("metodo,url,corpo,acesso", ENDPOINTS, ids=[f"{m} {u}" for m, u, _, _ in ENDPOINTS])
def test_tabela_de_acesso(cenario, metodo, url, corpo, acesso, quem):
    client, headers = cenario
    r = client.request(metodo, url, json=corpo, headers=headers[quem])

    if acesso == PUBLICO or (acesso == AMBOS and quem != "sem token") or quem == "funcionario":
        assert r.status_code not in (401, 403), r.text
        assert r.status_code < 500, r.text
    elif quem == "sem token":
        assert r.status_code == 401
    else:
        assert r.status_code == 403
        assert r.json() == {"detail": "Acesso negado para o seu perfil"}
