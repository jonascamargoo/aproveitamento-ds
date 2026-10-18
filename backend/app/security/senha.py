import bcrypt

from app.config import BCRYPT_ROUNDS


# O bcrypt considera no máximo 72 bytes da senha; cortar evita erro com senhas maiores.
def gerar_hash(senha: str) -> str:
    return bcrypt.hashpw(senha.encode()[:72], bcrypt.gensalt(BCRYPT_ROUNDS)).decode()


def verificar_senha(senha: str, hash_senha: str) -> bool:
    return bcrypt.checkpw(senha.encode()[:72], hash_senha.encode())
