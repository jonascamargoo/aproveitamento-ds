from sqlalchemy.orm import Session

from app.dtos.veiculo_dto import VeiculoDescricaoRequestDTO, VeiculoRequestDTO, VeiculoResponseDTO
from app.entities.veiculo import Veiculo
from app.exceptions import ConflitoException, NaoEncontradoException
from app.repositories.locacao_repository import LocacaoRepository
from app.repositories.veiculo_repository import VeiculoRepository


class VeiculoService:
    def __init__(self, db: Session):
        self.repository = VeiculoRepository(db)
        self.locacao_repository = LocacaoRepository(db)

    def listar(self) -> list[VeiculoResponseDTO]:
        return [VeiculoResponseDTO.model_validate(v) for v in self.repository.listar()]

    def buscar(self, id: int) -> VeiculoResponseDTO:
        return VeiculoResponseDTO.model_validate(self._buscar_entidade(id))

    def existe(self, placa: str) -> bool:
        return self.repository.existe_por_placa(placa)

    def cadastrar(self, dto: VeiculoRequestDTO) -> VeiculoResponseDTO:
        # R02 - placa única
        if self.repository.existe_por_placa(dto.placa):
            raise ConflitoException("Já existe um veículo com esta placa")
        # R03 - todo veículo novo começa disponível
        veiculo = Veiculo(placa=dto.placa, descricao=dto.descricao, disponivel=True)
        return VeiculoResponseDTO.model_validate(self.repository.salvar(veiculo))

    def alterar_descricao(self, id: int, dto: VeiculoDescricaoRequestDTO) -> VeiculoResponseDTO:
        veiculo = self._buscar_entidade(id)
        # R02 - na alteração, apenas a descrição pode ser modificada
        veiculo.descricao = dto.descricao
        return VeiculoResponseDTO.model_validate(self.repository.salvar(veiculo))

    def excluir(self, id: int) -> None:
        veiculo = self._buscar_entidade(id)
        # R09 - veículo com locações (em qualquer situação) não pode ser excluído
        if self.locacao_repository.existe_por_veiculo(id):
            raise ConflitoException("Veículo associado a locações não pode ser excluído")
        self.repository.excluir(veiculo)

    def _buscar_entidade(self, id: int) -> Veiculo:
        veiculo = self.repository.buscar_por_id(id)
        if veiculo is None:
            raise NaoEncontradoException("Veículo não encontrado")
        return veiculo
