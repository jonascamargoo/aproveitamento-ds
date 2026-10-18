from sqlalchemy.orm import Session

from app.dtos.locacao_dto import LocacaoRequestDTO, LocacaoResponseDTO
from app.entities.enums import Perfil, Situacao
from app.entities.locacao import Locacao
from app.entities.usuario import Usuario
from app.exceptions import AcessoNegadoException, ConflitoException, NaoEncontradoException, NegocioException
from app.repositories.locacao_repository import LocacaoRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.veiculo_repository import VeiculoRepository


class LocacaoService:
    def __init__(self, db: Session):
        self.repository = LocacaoRepository(db)
        self.veiculo_repository = VeiculoRepository(db)
        self.usuario_repository = UsuarioRepository(db)

    def criar(self, dto: LocacaoRequestDTO, funcionario_id: int) -> LocacaoResponseDTO:
        # R04 - só FUNCIONARIO cria (garantido no controller), o funcionário vem do JWT
        # e o usuário informado como cliente precisa ter perfil CLIENTE
        funcionario = self._buscar_usuario(funcionario_id, "Funcionário não encontrado")
        cliente = self._buscar_usuario(dto.clienteId, "Cliente não encontrado")
        if cliente.perfil != Perfil.CLIENTE:
            raise NegocioException("O usuário informado não possui perfil CLIENTE")

        veiculo = self.veiculo_repository.buscar_por_id(dto.veiculoId)
        if veiculo is None:
            raise NaoEncontradoException("Veículo não encontrado")
        # R05 - só veículo disponível; ao iniciar a locação ele fica indisponível
        if not veiculo.disponivel:
            raise ConflitoException("Veículo não está disponível")
        veiculo.disponivel = False

        # R06 - toda locação começa EM_ANDAMENTO
        locacao = Locacao(veiculo=veiculo, cliente=cliente, funcionario=funcionario, situacao=Situacao.EM_ANDAMENTO)
        return self._para_dto(self.repository.salvar(locacao))  # um único commit grava a locação e o veículo

    def listar_minhas(self, usuario_id: int, perfil: Perfil) -> list[LocacaoResponseDTO]:
        # R07 - cliente vê as locações em que é cliente; funcionário, as que é responsável
        if perfil == Perfil.CLIENTE:
            locacoes = self.repository.listar_por_cliente(usuario_id)
        else:
            locacoes = self.repository.listar_por_funcionario(usuario_id)
        return [self._para_dto(locacao) for locacao in locacoes]

    def buscar(self, id: int, usuario_id: int, perfil: Perfil) -> LocacaoResponseDTO:
        locacao = self._buscar_entidade(id)
        # R07
        if not self._participa(locacao, usuario_id, perfil):
            raise AcessoNegadoException("Você não tem acesso a esta locação")
        return self._para_dto(locacao)

    def finalizar(self, id: int, funcionario_id: int) -> LocacaoResponseDTO:
        locacao = self._buscar_entidade(id)
        # R08 - só o funcionário responsável, só locação EM_ANDAMENTO; o veículo volta a ficar disponível
        if locacao.funcionario_id != funcionario_id:
            raise AcessoNegadoException("Apenas o funcionário responsável pode finalizar esta locação")
        if locacao.situacao != Situacao.EM_ANDAMENTO:
            raise ConflitoException("Somente locações em andamento podem ser finalizadas")
        locacao.situacao = Situacao.FINALIZADA
        locacao.veiculo.disponivel = True
        return self._para_dto(self.repository.salvar(locacao))  # um único commit grava a locação e o veículo

    def _buscar_entidade(self, id: int) -> Locacao:
        locacao = self.repository.buscar_por_id(id)
        if locacao is None:
            raise NaoEncontradoException("Locação não encontrada")
        return locacao

    def _buscar_usuario(self, id: int, mensagem: str) -> Usuario:
        usuario = self.usuario_repository.buscar_por_id(id)
        if usuario is None:
            raise NaoEncontradoException(mensagem)
        return usuario

    @staticmethod
    def _participa(locacao: Locacao, usuario_id: int, perfil: Perfil) -> bool:
        if perfil == Perfil.CLIENTE:
            return locacao.cliente_id == usuario_id
        return locacao.funcionario_id == usuario_id

    @staticmethod
    def _para_dto(locacao: Locacao) -> LocacaoResponseDTO:
        return LocacaoResponseDTO(
            id=locacao.id,
            veiculoId=locacao.veiculo_id,
            situacao=locacao.situacao,
            clienteId=locacao.cliente_id,
            funcionarioId=locacao.funcionario_id,
        )
