import os
from pathlib import Path

# backend/ocar.db, independente da pasta de onde o uvicorn for iniciado
BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'ocar.db'}")

SECRET_KEY = os.getenv("SECRET_KEY", "ocar-chave-secreta-trocar-em-producao-0123456789")
JWT_ALGORITHM = "HS256"
JWT_EXPIRACAO_HORAS = 8

# Custo do hash bcrypt (os testes usam um valor menor para rodar mais rápido)
BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", "12"))
