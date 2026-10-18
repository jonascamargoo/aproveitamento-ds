"""Confere que o modelo de dados e os DTOs seguem exatamente o enunciado."""

import pytest
from dados import corpo_usuario
from sqlalchemy import inspect, text

from app.database import engine
from app.dtos.autenticacao_dto import AutenticacaoRequestDTO, AutenticacaoResponseDTO
from app.dtos.locacao_dto import LocacaoRequestDTO, LocacaoResponseDTO
from app.dtos.usuario_dto import UsuarioRequestDTO, UsuarioResponseDTO, UsuarioSenhaRequestDTO
from app.dtos.veiculo_dto import VeiculoRequestDTO, VeiculoResponseDTO
from app.entities import Locacao, Perfil, Situacao, Usuario, Veiculo
from app.repositories.usuario_repository import UsuarioRepository


def test_enums():
    assert [p.name for p in Perfil] == ["CLIENTE", "FUNCIONARIO"]
    assert [s.name for s in Situacao] == ["EM_ANDAMENTO", "FINALIZADA"]


@pytest.mark.parametrize(
    "entidade,atributos",
    [
        (Usuario, {"id", "login", "senha", "perfil"}),
        (Veiculo, {"id", "placa", "descricao", "disponivel"}),
        (Locacao, {"id", "veiculo", "situacao", "cliente", "funcionario"}),
    ],
)
def test_atributos_das_entidades(entidade, atributos):
    mapper = inspect(entidade)
    colunas = {c.key for c in mapper.column_attrs}
    relacionamentos = {r.key for r in mapper.relationships}
    # as colunas *_id são as chaves estrangeiras dos relacionamentos (equivalente ao @JoinColumn)
    fks = {f"{r}_id" for r in relacionamentos}
    assert (colunas - fks) | relacionamentos == atributos


def test_relacionamentos_da_locacao_sao_muitos_para_um():
    relacionamentos = inspect(Locacao).relationships
    assert {r.key: r.direction.name for r in relacionamentos} == {
        "veiculo": "MANYTOONE",
        "cliente": "MANYTOONE",
        "funcionario": "MANYTOONE",
    }
    assert relacionamentos["veiculo"].mapper.class_ is Veiculo
    assert relacionamentos["cliente"].mapper.class_ is Usuario
    assert relacionamentos["funcionario"].mapper.class_ is Usuario


@pytest.mark.parametrize(
    "dto,campos",
    [
        (UsuarioRequestDTO, ["login", "senha", "perfil"]),
        (UsuarioResponseDTO, ["id", "login", "perfil"]),
        (UsuarioSenhaRequestDTO, ["senha"]),
        (VeiculoRequestDTO, ["placa", "descricao"]),
        (VeiculoResponseDTO, ["id", "placa", "descricao", "disponivel"]),
        (LocacaoRequestDTO, ["veiculoId", "clienteId"]),
        (LocacaoResponseDTO, ["id", "veiculoId", "situacao", "clienteId", "funcionarioId"]),
        (AutenticacaoRequestDTO, ["login", "senha"]),
        (AutenticacaoResponseDTO, ["token"]),
    ],
)
def test_campos_dos_dtos(dto, campos):
    assert list(dto.model_fields) == campos


def test_todos_os_campos_sao_obrigatorios_no_banco(client):
    insp = inspect(engine)
    for tabela in ("usuario", "veiculo", "locacao"):
        for coluna in insp.get_columns(tabela):
            assert coluna["nullable"] is False, f"{tabela}.{coluna['name']} aceita NULL"


def test_login_e_placa_sao_unicos_no_banco(client):
    insp = inspect(engine)
    assert {"login"} in [set(u["column_names"]) for u in insp.get_unique_constraints("usuario")]
    assert {"placa"} in [set(u["column_names"]) for u in insp.get_unique_constraints("veiculo")]


def test_chaves_estrangeiras_da_locacao(client):
    fks = {fk["constrained_columns"][0]: fk["referred_table"] for fk in inspect(engine).get_foreign_keys("locacao")}
    assert fks == {"veiculo_id": "veiculo", "cliente_id": "usuario", "funcionario_id": "usuario"}


def test_enums_gravados_como_texto(client, api, cliente, funcionario):
    veiculo = api.veiculo(funcionario.headers)
    api.locacao(funcionario.headers, veiculo["id"], cliente.id)
    with engine.connect() as conn:
        perfis = conn.execute(text("SELECT perfil FROM usuario ORDER BY id")).scalars().all()
        situacao = conn.execute(text("SELECT situacao FROM locacao")).scalar_one()
    assert perfis == ["CLIENTE", "FUNCIONARIO"]  # EnumType.STRING, não ordinal
    assert situacao == "EM_ANDAMENTO"


def test_duplicidade_barrada_pelo_banco_vira_409(client, api, monkeypatch):
    """Simula duas requisições simultâneas: a checagem do service passa e o UNIQUE do banco barra."""
    api.cadastrar("maria", "CLIENTE")
    monkeypatch.setattr(UsuarioRepository, "existe_por_login", lambda self, login: False)
    r = client.post("/usuarios", json=corpo_usuario(login="maria"))
    assert r.status_code == 409
    assert r.json() == {"detail": "Registro duplicado ou inválido"}
    # a API continua funcionando depois do erro
    monkeypatch.undo()
    assert client.get("/usuarios/existe", params={"login": "maria"}).json() is True
    assert client.post("/usuarios", json=corpo_usuario(login="ana")).status_code == 201
