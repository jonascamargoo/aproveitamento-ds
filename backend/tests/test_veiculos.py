import pytest
from dados import contem, corpo_veiculo, sem


def test_cadastrar(client, funcionario):
    r = client.post("/veiculos", json=corpo_veiculo(), headers=funcionario.headers)
    assert r.status_code == 201
    assert contem(r.json(), id=1, placa="ABC1D23", descricao="Toyota Corolla", disponivel=True)


def test_r03_disponivel_enviado_e_ignorado(client, funcionario):
    r = client.post("/veiculos", json=corpo_veiculo(disponivel=False, id=50), headers=funcionario.headers)
    assert r.status_code == 201
    assert contem(r.json(), id=1, disponivel=True)


def test_r02_placa_duplicada(client, api, funcionario):
    api.veiculo(funcionario.headers, placa="ABC1D23")
    r = client.post("/veiculos", json=corpo_veiculo(placa="ABC1D23", descricao="Outro"), headers=funcionario.headers)
    assert r.status_code == 409
    assert r.json() == {"detail": "Já existe um veículo com esta placa"}
    r = client.post("/veiculos", json=corpo_veiculo(placa=" ABC1D23 "), headers=funcionario.headers)
    assert r.status_code == 409


def test_espacos_nas_pontas_sao_removidos(client, funcionario):
    r = client.post("/veiculos", json=corpo_veiculo(placa="  XYZ9A99 ", descricao=" Fiat Uno  "), headers=funcionario.headers)
    assert contem(r.json(), placa="XYZ9A99", descricao="Fiat Uno")


@pytest.mark.parametrize(
    "corpo",
    [
        {},
        sem(corpo_veiculo(), "placa"),
        sem(corpo_veiculo(), "descricao"),
        corpo_veiculo(placa=""),
        corpo_veiculo(placa="   "),
        corpo_veiculo(descricao=""),
        corpo_veiculo(descricao="   "),
        corpo_veiculo(placa="X" * 21),
        corpo_veiculo(descricao="X" * 256),
        corpo_veiculo(placa=None),
    ],
)
def test_cadastrar_campos_obrigatorios_e_invalidos(client, funcionario, corpo):
    assert client.post("/veiculos", json=corpo, headers=funcionario.headers).status_code == 422


def test_listar(client, api, funcionario):
    assert client.get("/veiculos", headers=funcionario.headers).json() == []
    v1 = api.veiculo(funcionario.headers, placa="AAA1111", descricao="Um")
    v2 = api.veiculo(funcionario.headers, placa="BBB2222", descricao="Dois")
    assert client.get("/veiculos", headers=funcionario.headers).json() == [v1, v2]


def test_buscar_por_id(client, api, funcionario):
    veiculo = api.veiculo(funcionario.headers)
    assert client.get(f"/veiculos/{veiculo['id']}", headers=funcionario.headers).json() == veiculo


@pytest.mark.parametrize("id,status", [("99", 404), ("0", 404), ("-1", 404), ("abc", 422), ("1.5", 422)])
def test_buscar_id_inexistente_ou_invalido(client, funcionario, id, status):
    assert client.get(f"/veiculos/{id}", headers=funcionario.headers).status_code == status


def test_existe(client, api, funcionario):
    api.veiculo(funcionario.headers, placa="ABC1D23")
    assert client.get("/veiculos/existe", params={"placa": "ABC1D23"}, headers=funcionario.headers).json() is True
    assert client.get("/veiculos/existe", params={"placa": "ZZZ0000"}, headers=funcionario.headers).json() is False
    assert client.get("/veiculos/existe", headers=funcionario.headers).status_code == 422


def test_r02_alterar_so_muda_a_descricao(client, api, funcionario):
    veiculo = api.veiculo(funcionario.headers)
    r = client.patch(
        f"/veiculos/{veiculo['id']}",
        json={"descricao": "Corolla XEi", "placa": "ZZZ9999", "disponivel": False, "id": 7},
        headers=funcionario.headers,
    )
    assert r.status_code == 200
    esperado = {**veiculo, "descricao": "Corolla XEi"}
    assert r.json() == esperado
    assert client.get(f"/veiculos/{veiculo['id']}", headers=funcionario.headers).json() == esperado


@pytest.mark.parametrize("corpo", [{}, {"descricao": ""}, {"descricao": "  "}, {"placa": "ZZZ9999"}])
def test_alterar_descricao_invalida(client, api, funcionario, corpo):
    veiculo = api.veiculo(funcionario.headers)
    assert client.patch(f"/veiculos/{veiculo['id']}", json=corpo, headers=funcionario.headers).status_code == 422


def test_alterar_veiculo_inexistente(client, funcionario):
    r = client.patch("/veiculos/99", json={"descricao": "X"}, headers=funcionario.headers)
    assert r.status_code == 404
    assert r.json() == {"detail": "Veículo não encontrado"}


def test_excluir(client, api, funcionario):
    veiculo = api.veiculo(funcionario.headers)
    r = client.delete(f"/veiculos/{veiculo['id']}", headers=funcionario.headers)
    assert r.status_code == 204
    assert r.content == b""
    assert client.get(f"/veiculos/{veiculo['id']}", headers=funcionario.headers).status_code == 404
    assert client.delete(f"/veiculos/{veiculo['id']}", headers=funcionario.headers).status_code == 404
    # a placa fica livre de novo
    api.veiculo(funcionario.headers)


def test_excluir_inexistente(client, funcionario):
    assert client.delete("/veiculos/99", headers=funcionario.headers).status_code == 404
