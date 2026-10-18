import pytest
from dados import contem, corpo_locacao, sem


@pytest.fixture
def veiculo(api, funcionario) -> dict:
    return api.veiculo(funcionario.headers)


def disponivel(client, headers, veiculo_id) -> bool:
    return client.get(f"/veiculos/{veiculo_id}", headers=headers).json()["disponivel"]


def test_criar(client, cliente, funcionario, veiculo):
    r = client.post("/locacoes", json=corpo_locacao(veiculo["id"], cliente.id), headers=funcionario.headers)
    assert r.status_code == 201
    assert contem(
        r.json(),
        id=1,
        veiculoId=veiculo["id"],
        situacao="EM_ANDAMENTO",  # R06
        clienteId=cliente.id,
        funcionarioId=funcionario.id,  # R04: veio do JWT
    )


def test_criar_com_ids_em_string_como_o_insomnia(client, cliente, funcionario, veiculo):
    corpo = corpo_locacao(str(veiculo["id"]), str(cliente.id))
    assert client.post("/locacoes", json=corpo, headers=funcionario.headers).status_code == 201


def test_r04_funcionario_id_do_corpo_e_ignorado(client, api, cliente, funcionario, veiculo):
    outro = api.usuario("ana", "FUNCIONARIO")
    corpo = corpo_locacao(veiculo["id"], cliente.id, funcionarioId=outro.id, situacao="FINALIZADA")
    r = client.post("/locacoes", json=corpo, headers=funcionario.headers)
    assert r.json()["funcionarioId"] == funcionario.id
    assert r.json()["situacao"] == "EM_ANDAMENTO"


def test_r04_cliente_precisa_ter_perfil_cliente(client, api, funcionario, veiculo):
    outro = api.usuario("ana", "FUNCIONARIO")
    r = client.post("/locacoes", json=corpo_locacao(veiculo["id"], outro.id), headers=funcionario.headers)
    assert r.status_code == 400
    assert r.json() == {"detail": "O usuário informado não possui perfil CLIENTE"}
    # o próprio funcionário também não pode ser o cliente
    corpo = corpo_locacao(veiculo["id"], funcionario.id)
    assert client.post("/locacoes", json=corpo, headers=funcionario.headers).status_code == 400
    # e o veículo continua disponível
    assert disponivel(client, funcionario.headers, veiculo["id"]) is True


def test_criar_com_cliente_ou_veiculo_inexistente(client, cliente, funcionario, veiculo):
    r = client.post("/locacoes", json=corpo_locacao(veiculo["id"], 99), headers=funcionario.headers)
    assert r.status_code == 404
    assert r.json() == {"detail": "Cliente não encontrado"}
    r = client.post("/locacoes", json=corpo_locacao(99, cliente.id), headers=funcionario.headers)
    assert r.status_code == 404
    assert r.json() == {"detail": "Veículo não encontrado"}


@pytest.mark.parametrize(
    "corpo",
    [{}, sem(corpo_locacao(1, 1), "clienteId"), sem(corpo_locacao(1, 1), "veiculoId"), corpo_locacao("abc", 1), corpo_locacao(None, 1)],
)
def test_criar_campos_obrigatorios(client, funcionario, corpo):
    assert client.post("/locacoes", json=corpo, headers=funcionario.headers).status_code == 422


def test_r05_veiculo_fica_indisponivel_e_nao_pode_ser_locado_de_novo(client, api, cliente, funcionario, veiculo):
    api.locacao(funcionario.headers, veiculo["id"], cliente.id)
    assert disponivel(client, funcionario.headers, veiculo["id"]) is False

    outro_cliente = api.usuario("ana", "CLIENTE")
    corpo = corpo_locacao(veiculo["id"], outro_cliente.id)
    r = client.post("/locacoes", json=corpo, headers=funcionario.headers)
    assert r.status_code == 409
    assert r.json() == {"detail": "Veículo não está disponível"}

    # outro funcionário também não consegue
    outro_func = api.usuario("pedro", "FUNCIONARIO")
    assert client.post("/locacoes", json=corpo, headers=outro_func.headers).status_code == 409

    # mas outro veículo pode
    outro_veiculo = api.veiculo(funcionario.headers, placa="XYZ9A99")
    api.locacao(funcionario.headers, outro_veiculo["id"], outro_cliente.id)


def test_r07_cada_um_lista_so_as_suas(client, api, funcionario):
    maria = api.usuario("maria", "CLIENTE")
    ana = api.usuario("ana", "CLIENTE")
    pedro = api.usuario("pedro", "FUNCIONARIO")
    v1 = api.veiculo(funcionario.headers, placa="AAA1111")
    v2 = api.veiculo(funcionario.headers, placa="BBB2222")
    v3 = api.veiculo(funcionario.headers, placa="CCC3333")

    l1 = api.locacao(funcionario.headers, v1["id"], maria.id)
    l2 = api.locacao(pedro.headers, v2["id"], maria.id)
    l3 = api.locacao(funcionario.headers, v3["id"], ana.id)

    def ids(usuario):
        r = client.get("/locacoes/minhas", headers=usuario.headers)
        assert r.status_code == 200
        return [locacao["id"] for locacao in r.json()]

    assert ids(maria) == [l1["id"], l2["id"]]
    assert ids(ana) == [l3["id"]]
    assert ids(funcionario) == [l1["id"], l3["id"]]
    assert ids(pedro) == [l2["id"]]
    assert ids(api.usuario("sem", "CLIENTE")) == []


def test_r07_consultar_por_id(client, api, cliente, funcionario, veiculo):
    locacao = api.locacao(funcionario.headers, veiculo["id"], cliente.id)
    outro_cliente = api.usuario("ana", "CLIENTE")
    outro_func = api.usuario("pedro", "FUNCIONARIO")
    url = f"/locacoes/{locacao['id']}"

    assert client.get(url, headers=cliente.headers).json() == locacao
    assert client.get(url, headers=funcionario.headers).json() == locacao

    r = client.get(url, headers=outro_cliente.headers)
    assert r.status_code == 403
    assert r.json() == {"detail": "Você não tem acesso a esta locação"}
    assert client.get(url, headers=outro_func.headers).status_code == 403


@pytest.mark.parametrize("id,status", [("99", 404), ("abc", 422)])
def test_consultar_inexistente_ou_invalido(client, funcionario, id, status):
    assert client.get(f"/locacoes/{id}", headers=funcionario.headers).status_code == status


def test_r08_finalizar(client, api, cliente, funcionario, veiculo):
    locacao = api.locacao(funcionario.headers, veiculo["id"], cliente.id)
    r = client.patch(f"/locacoes/{locacao['id']}/finalizar", headers=funcionario.headers)
    assert r.status_code == 200
    assert r.json() == {**locacao, "situacao": "FINALIZADA"}
    assert disponivel(client, funcionario.headers, veiculo["id"]) is True
    # o cliente vê a locação finalizada
    assert client.get(f"/locacoes/{locacao['id']}", headers=cliente.headers).json()["situacao"] == "FINALIZADA"


def test_r08_nao_finaliza_duas_vezes(client, api, cliente, funcionario, veiculo):
    locacao = api.locacao(funcionario.headers, veiculo["id"], cliente.id)
    client.patch(f"/locacoes/{locacao['id']}/finalizar", headers=funcionario.headers)
    r = client.patch(f"/locacoes/{locacao['id']}/finalizar", headers=funcionario.headers)
    assert r.status_code == 409
    assert r.json() == {"detail": "Somente locações em andamento podem ser finalizadas"}


def test_r08_so_o_funcionario_responsavel_finaliza(client, api, cliente, funcionario, veiculo):
    locacao = api.locacao(funcionario.headers, veiculo["id"], cliente.id)
    outro_func = api.usuario("pedro", "FUNCIONARIO")
    r = client.patch(f"/locacoes/{locacao['id']}/finalizar", headers=outro_func.headers)
    assert r.status_code == 403
    assert r.json() == {"detail": "Apenas o funcionário responsável pode finalizar esta locação"}
    # nada mudou
    assert client.get(f"/locacoes/{locacao['id']}", headers=funcionario.headers).json()["situacao"] == "EM_ANDAMENTO"
    assert disponivel(client, funcionario.headers, veiculo["id"]) is False


def test_finalizar_inexistente(client, funcionario):
    assert client.patch("/locacoes/99/finalizar", headers=funcionario.headers).status_code == 404


def test_veiculo_pode_ser_locado_de_novo_depois_de_finalizar(client, api, cliente, funcionario, veiculo):
    primeira = api.locacao(funcionario.headers, veiculo["id"], cliente.id)
    client.patch(f"/locacoes/{primeira['id']}/finalizar", headers=funcionario.headers)
    segunda = api.locacao(funcionario.headers, veiculo["id"], cliente.id)
    assert segunda["id"] == primeira["id"] + 1
    assert disponivel(client, funcionario.headers, veiculo["id"]) is False
    situacoes = [l["situacao"] for l in client.get("/locacoes/minhas", headers=cliente.headers).json()]
    assert situacoes == ["FINALIZADA", "EM_ANDAMENTO"]


def test_r09_nao_exclui_veiculo_com_locacao_em_andamento_ou_finalizada(client, api, cliente, funcionario, veiculo):
    locacao = api.locacao(funcionario.headers, veiculo["id"], cliente.id)
    r = client.delete(f"/veiculos/{veiculo['id']}", headers=funcionario.headers)
    assert r.status_code == 409
    assert r.json() == {"detail": "Veículo associado a locações não pode ser excluído"}

    client.patch(f"/locacoes/{locacao['id']}/finalizar", headers=funcionario.headers)
    assert client.delete(f"/veiculos/{veiculo['id']}", headers=funcionario.headers).status_code == 409
    assert client.get(f"/veiculos/{veiculo['id']}", headers=funcionario.headers).status_code == 200


def test_alterar_descricao_de_veiculo_locado_nao_muda_disponibilidade(client, api, cliente, funcionario, veiculo):
    api.locacao(funcionario.headers, veiculo["id"], cliente.id)
    r = client.patch(f"/veiculos/{veiculo['id']}", json={"descricao": "Nova"}, headers=funcionario.headers)
    assert r.json()["disponivel"] is False
