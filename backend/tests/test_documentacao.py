"""O Swagger (/docs) precisa funcionar sem internet: nada pode vir de fora."""

import re


def test_swagger_nao_depende_da_internet(client):
    r = client.get("/docs")
    assert r.status_code == 200
    assert "http://" not in r.text and "https://" not in r.text
    arquivos = re.findall(r'(?:src|href)="([^"]+)"', r.text)
    assert len(arquivos) == 3  # js, css e favicon
    for arquivo in arquivos:
        assert client.get(arquivo).status_code == 200, arquivo


def test_swagger_le_a_especificacao_da_api(client):
    assert client.get("/openapi.json").json()["info"]["title"] == "OCar API"
