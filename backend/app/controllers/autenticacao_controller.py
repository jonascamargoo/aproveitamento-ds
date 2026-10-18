from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dtos.autenticacao_dto import AutenticacaoRequestDTO, AutenticacaoResponseDTO
from app.services.autenticacao_service import AutenticacaoService

router = APIRouter(tags=["Autenticação"])


@router.post("/login")
def login(dto: AutenticacaoRequestDTO, db: Session = Depends(get_db)) -> AutenticacaoResponseDTO:
    return AutenticacaoService(db).autenticar(dto)
