"""Confere a arquitetura em camadas (Figura 01) olhando os imports de cada pacote.

Controller <-DTO-> Service <-Entity-> Repository
"""

import ast
from pathlib import Path

import pytest

APP = Path(__file__).parent.parent / "app"
ENTIDADES = ["app.entities.usuario", "app.entities.veiculo", "app.entities.locacao"]  # enums são liberados

# pacote -> o que ele NÃO pode importar
PROIBIDOS = {
    # controller só conversa com DTOs e services
    "controllers": ["app.repositories", *ENTIDADES],
    # service não sabe nada de HTTP
    "services": ["fastapi", "starlette", "app.controllers", "app.security.dependencias"],
    # repository só acessa o banco
    "repositories": ["fastapi", "app.dtos", "app.services", "app.controllers", "app.security"],
    "entities": ["fastapi", "app.dtos", "app.services", "app.repositories", "app.controllers", "app.security"],
    # DTO não depende de banco nem de entidades
    "dtos": ["fastapi", "sqlalchemy", "app.services", "app.repositories", "app.controllers", *ENTIDADES],
}


def imports(arquivo: Path) -> set[str]:
    nomes = set()
    for no in ast.walk(ast.parse(arquivo.read_text())):
        if isinstance(no, ast.Import):
            nomes |= {alias.name for alias in no.names}
        elif isinstance(no, ast.ImportFrom) and no.module:
            nomes.add(no.module)
    return nomes


@pytest.mark.parametrize("pacote", PROIBIDOS)
def test_camada_nao_importa_o_que_nao_deve(pacote):
    violacoes = [
        f"{pacote}/{arquivo.name} importa {nome}"
        for arquivo in sorted((APP / pacote).glob("*.py"))
        for nome in imports(arquivo)
        for proibido in PROIBIDOS[pacote]
        if nome == proibido or nome.startswith(proibido + ".")
    ]
    assert violacoes == []
