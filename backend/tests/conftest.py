import os
from dataclasses import dataclass
from pathlib import Path

# Precisa vir antes de importar o app: banco próprio dos testes e bcrypt mais rápido
BANCO_TESTE = Path(__file__).parent / "test_ocar.db"
os.environ["DATABASE_URL"] = f"sqlite:///{BANCO_TESTE}"
os.environ["BCRYPT_ROUNDS"] = "4"

import pytest
from dados import SENHA, corpo_locacao, corpo_usuario, corpo_veiculo
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


@dataclass
class UsuarioTeste:
    id: int
    login: str
    headers: dict


class Api:
    """Atalhos para montar o cenário dos testes."""

    def __init__(self, client: TestClient):
        self.client = client

    def cadastrar(self, login: str, perfil: str, senha: str = SENHA) -> int:
        r = self.client.post("/usuarios", json=corpo_usuario(login=login, perfil=perfil, senha=senha))
        assert r.status_code == 201, r.text
        return r.json()["id"]

    def logar(self, login: str, senha: str = SENHA) -> dict:
        r = self.client.post("/login", json={"login": login, "senha": senha})
        assert r.status_code == 200, r.text
        return {"Authorization": f"Bearer {r.json()['token']}"}

    def usuario(self, login: str, perfil: str) -> UsuarioTeste:
        id = self.cadastrar(login, perfil)
        return UsuarioTeste(id, login, self.logar(login))

    def veiculo(self, headers: dict, **campos) -> dict:
        r = self.client.post("/veiculos", json=corpo_veiculo(**campos), headers=headers)
        assert r.status_code == 201, r.text
        return r.json()

    def locacao(self, headers: dict, veiculo_id: int, cliente_id: int) -> dict:
        r = self.client.post("/locacoes", json=corpo_locacao(veiculo_id, cliente_id), headers=headers)
        assert r.status_code == 201, r.text
        return r.json()


@pytest.fixture
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c


@pytest.fixture
def api(client) -> Api:
    return Api(client)


@pytest.fixture
def cliente(api) -> UsuarioTeste:
    return api.usuario("maria", "CLIENTE")


@pytest.fixture
def funcionario(api) -> UsuarioTeste:
    return api.usuario("jose", "FUNCIONARIO")


@pytest.fixture(autouse=True, scope="session")
def apagar_banco_de_teste():
    yield
    engine.dispose()
    BANCO_TESTE.unlink(missing_ok=True)
