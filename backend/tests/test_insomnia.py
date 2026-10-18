"""Executa a coleção do Insomnia da banca contra a API, em ordem lógica e com o banco vazio.

É pulado se o arquivo .yaml não estiver na raiz do projeto.
"""

import json
import re
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")

COLECAO = Path(__file__).parent.parent.parent / "Aproveitamento_de_Estudo_Avaliacao_Pratica_Parte_I.yaml"


@pytest.fixture
def insomnia(client):
    if not COLECAO.exists():
        pytest.skip(f"{COLECAO.name} não encontrado")
    recursos = yaml.safe_load(COLECAO.read_text())["resources"]
    env = dict(next(r for r in recursos if r["_type"] == "environment")["data"])
    requisicoes = {r["name"]: r for r in recursos if r["_type"] == "request"}

    def render(texto: str) -> str:
        return re.sub(r"\{\{\s*_\.(\w+)\s*\}\}", lambda m: str(env[m.group(1)]), texto)

    def executar(nome: str, status: int):
        req = requisicoes[nome]
        headers = {h["name"]: render(h["value"]) for h in req.get("headers", [])}
        corpo = render(req["body"]["text"]) if req.get("body", {}).get("text") else None
        r = client.request(req["method"], render(req["url"]), content=corpo, headers=headers)
        assert r.status_code == status, f"{nome}: {r.status_code} {r.text}"
        return r

    return executar, env, requisicoes


def test_colecao_tem_os_16_endpoints(insomnia):
    _, _, requisicoes = insomnia
    endpoints = {(r["method"], re.sub(r"\?.*", "", r["url"])) for r in requisicoes.values()}
    assert len(endpoints) == 16


def test_colecao_completa(insomnia, client):
    executar, env, _ = insomnia

    assert executar("Cadastrar - Cliente", 201).json()["id"] == 1
    assert executar("Cadastrar - Funcionario", 201).json()["id"] == 2
    assert executar("Verificar existencia de usuario", 200).json() is True
    env["token_cliente"] = executar("Login - Cliente", 200).json()["token"]
    env["token_funcionario"] = executar("Login - Funcionario", 200).json()["token"]
    assert executar("Meus dados - Cliente", 200).json()["perfil"] == "CLIENTE"
    assert executar("Meus dados - Funcionario", 200).json()["perfil"] == "FUNCIONARIO"
    assert len(executar("Listar clientes - Funcionario", 200).json()) == 1

    assert executar("Cadastrar veiculo - Funcionario", 201).json()["disponivel"] is True
    # a coleção exclui o veículo 2, que precisa existir e não ter locação
    headers = {"Authorization": f"Bearer {env['token_funcionario']}"}
    client.post("/veiculos", json={"placa": "XYZ9A99", "descricao": "Fiat Uno"}, headers=headers)

    assert len(executar("Listar veiculos - Funcionario", 200).json()) == 2
    executar("Consultar veiculo por ID - Cliente", 200)
    executar("Consultar veiculo por ID - Funcionario", 200)
    assert executar("Verificar existencia por placa - Funcionario", 200).json() is True
    assert executar("Alterar descricao - Funcionario", 200).json()["descricao"] == env["descricao_atualizada"]
    executar("Excluir veiculo - Funcionario", 204)

    locacao = executar("Criar locacao - Funcionario", 201).json()
    assert locacao == {"id": 1, "veiculoId": 1, "situacao": "EM_ANDAMENTO", "clienteId": 1, "funcionarioId": 2}
    assert executar("Minhas locacoes - Cliente", 200).json() == [locacao]
    assert executar("Consultar locacao por ID - Cliente", 200).json() == locacao
    assert executar("Minhas locacoes - Funcionario", 200).json() == [locacao]
    assert executar("Consultar locacao por ID - Funcionario", 200).json() == locacao
    assert executar("Finalizar locacao - Funcionario", 200).json()["situacao"] == "FINALIZADA"

    executar("Alterar senha - Cliente", 204)
    executar("Alterar senha - Funcionario", 204)

    # casos que a banca pode testar para ver as regras
    env["veiculo_exclusao_id"] = 1
    executar("Excluir veiculo - Funcionario", 409)  # R09
    executar("Cadastrar - Cliente", 409)  # R01
    executar("Cadastrar veiculo - Funcionario", 409)  # R02
    executar("Finalizar locacao - Funcionario", 409)  # R08
    env["token_funcionario"] = env["token_cliente"]
    executar("Listar veiculos - Funcionario", 403)
    executar("Criar locacao - Funcionario", 403)
    env["token_cliente"] = ""
    executar("Meus dados - Cliente", 401)
