import jwt
import pytest
from dados import contem, corpo_usuario, sem
from sqlalchemy import text

from app.database import engine


def test_cadastrar_devolve_dto_sem_senha(client):
    r = client.post("/usuarios", json=corpo_usuario(login="maria", perfil="CLIENTE"))
    assert r.status_code == 201
    assert contem(r.json(), id=1, login="maria", perfil="CLIENTE")
    assert "senha" not in r.json()


def test_cadastrar_funcionario(client):
    r = client.post("/usuarios", json=corpo_usuario(login="jose", perfil="FUNCIONARIO"))
    assert r.status_code == 201
    assert r.json()["perfil"] == "FUNCIONARIO"


def test_r01_login_duplicado(client, cliente):
    r = client.post("/usuarios", json=corpo_usuario(login="maria", perfil="FUNCIONARIO"))
    assert r.status_code == 409
    assert r.json() == {"detail": "Já existe um usuário com este login"}
    # espaços nas pontas são removidos, então continua sendo duplicado
    assert client.post("/usuarios", json=corpo_usuario(login="  maria  ")).status_code == 409


def test_login_diferencia_maiusculas(client, cliente):
    assert client.post("/usuarios", json=corpo_usuario(login="Maria")).status_code == 201


@pytest.mark.parametrize(
    "corpo",
    [
        {},
        sem(corpo_usuario(), "login"),
        sem(corpo_usuario(), "senha"),
        sem(corpo_usuario(), "perfil"),
        corpo_usuario(login=""),
        corpo_usuario(login="   "),
        corpo_usuario(senha=""),
        corpo_usuario(perfil="ADMIN"),
        corpo_usuario(perfil="cliente"),
        corpo_usuario(perfil=None),
        corpo_usuario(login="x" * 101),
    ],
)
def test_cadastrar_campos_obrigatorios_e_invalidos(client, corpo):
    r = client.post("/usuarios", json=corpo)
    assert r.status_code == 422
    assert isinstance(r.json()["detail"], list)


def test_cadastrar_corpo_que_nao_e_json(client):
    r = client.post("/usuarios", content="isso não é json", headers={"Content-Type": "application/json"})
    assert r.status_code == 422


def test_campos_extras_sao_ignorados(client):
    r = client.post("/usuarios", json=corpo_usuario(id=99, admin=True))
    assert r.status_code == 201
    assert contem(r.json(), id=1)
    assert "admin" not in r.json()


def test_senha_guardada_com_hash_bcrypt(client, cliente):
    with engine.connect() as conn:
        senha = conn.execute(text("SELECT senha FROM usuario WHERE login = 'maria'")).scalar_one()
    assert senha != "123"
    assert senha.startswith("$2b$")


def test_existe(client, cliente):
    assert client.get("/usuarios/existe", params={"login": "maria"}).json() is True
    assert client.get("/usuarios/existe", params={"login": "joao"}).json() is False
    assert client.get("/usuarios/existe", params={"login": ""}).json() is False
    assert client.get("/usuarios/existe").status_code == 422


def test_login_devolve_token_com_id_login_e_perfil(client, cliente):
    r = client.post("/login", json={"login": "maria", "senha": "123"})
    assert r.status_code == 200
    assert list(r.json()) == ["token"]
    payload = jwt.decode(r.json()["token"], options={"verify_signature": False})
    assert payload["sub"] == str(cliente.id)
    assert payload["login"] == "maria"
    assert payload["perfil"] == "CLIENTE"
    assert "exp" in payload


def test_login_aceita_espacos_nas_pontas_do_login(client, cliente):
    assert client.post("/login", json={"login": " maria ", "senha": "123"}).status_code == 200


@pytest.mark.parametrize(
    "corpo",
    [
        {"login": "maria", "senha": "errada"},
        {"login": "ninguem", "senha": "123"},
        {"login": "maria", "senha": "123 "},
    ],
)
def test_login_invalido(client, cliente, corpo):
    r = client.post("/login", json=corpo)
    assert r.status_code == 401
    assert r.json() == {"detail": "Login ou senha inválidos"}


@pytest.mark.parametrize("corpo", [{}, {"login": "maria"}, {"senha": "123"}, {"login": "", "senha": ""}])
def test_login_campos_obrigatorios(client, corpo):
    assert client.post("/login", json=corpo).status_code == 422


def test_meus_dados(client, cliente, funcionario):
    assert contem(client.get("/usuarios/meus-dados", headers=cliente.headers).json(), id=cliente.id, login="maria", perfil="CLIENTE")
    assert contem(
        client.get("/usuarios/meus-dados", headers=funcionario.headers).json(), id=funcionario.id, login="jose", perfil="FUNCIONARIO"
    )


def test_alterar_senha(client, cliente):
    r = client.patch("/usuarios/senha", json={"senha": "nova"}, headers=cliente.headers)
    assert r.status_code == 204
    assert r.content == b""
    assert client.post("/login", json={"login": "maria", "senha": "123"}).status_code == 401
    assert client.post("/login", json={"login": "maria", "senha": "nova"}).status_code == 200
    # o token emitido antes continua valendo
    assert client.get("/usuarios/meus-dados", headers=cliente.headers).status_code == 200


def test_alterar_senha_so_altera_a_propria(client, cliente, funcionario):
    client.patch("/usuarios/senha", json={"senha": "nova"}, headers=cliente.headers)
    assert client.post("/login", json={"login": "jose", "senha": "123"}).status_code == 200


@pytest.mark.parametrize("corpo", [{}, {"senha": ""}, {"senha": None}])
def test_alterar_senha_invalida(client, cliente, corpo):
    assert client.patch("/usuarios/senha", json=corpo, headers=cliente.headers).status_code == 422


def test_senha_longa_e_com_acentos(client, api):
    senha = "çãõ€" * 30  # mais de 72 bytes
    api.cadastrar("longa", "CLIENTE", senha=senha)
    assert client.post("/login", json={"login": "longa", "senha": senha}).status_code == 200


def test_listar_clientes_traz_so_clientes(client, api, funcionario):
    id_ana = api.cadastrar("ana", "CLIENTE")
    api.cadastrar("pedro", "FUNCIONARIO")
    id_bia = api.cadastrar("bia", "CLIENTE")
    r = client.get("/usuarios/clientes", headers=funcionario.headers)
    assert r.status_code == 200
    assert [(u["id"], u["login"], u["perfil"]) for u in r.json()] == [(id_ana, "ana", "CLIENTE"), (id_bia, "bia", "CLIENTE")]


def test_listar_clientes_vazio(client, funcionario):
    assert client.get("/usuarios/clientes", headers=funcionario.headers).json() == []
