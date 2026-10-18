"""Corpos padrão das requisições usados nos testes.

Se o professor pedir um campo novo obrigatório, inclua-o aqui (ex.: "cor": "Prata" no veículo)
e todos os testes passam a enviá-lo.
"""

SENHA = "123"


def corpo_usuario(**campos) -> dict:
    return {"login": "maria", "senha": SENHA, "perfil": "CLIENTE", **campos}


def corpo_veiculo(**campos) -> dict:
    return {"placa": "ABC1D23", "descricao": "Toyota Corolla", **campos}


def corpo_locacao(veiculo_id, cliente_id, **campos) -> dict:
    return {"veiculoId": veiculo_id, "clienteId": cliente_id, **campos}


def sem(corpo: dict, campo: str) -> dict:
    """Cópia do corpo sem um campo (para testar campo obrigatório)."""
    return {k: v for k, v in corpo.items() if k != campo}


def contem(resposta: dict, **esperado) -> bool:
    """True se a resposta tem esses campos com esses valores (ignora campos a mais)."""
    return esperado.items() <= resposta.items()
