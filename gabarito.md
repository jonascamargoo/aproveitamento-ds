# Gabarito: os 4 pedidos que faltavam no simulado

São os tipos de pedido que citei como prováveis e que não estavam no [`simulado.md`](simulado.md). Cada um tem o pedido, o que você aprende com ele, o passo a passo explicado e como conferir o resultado. Os outros tipos já têm gabarito no próprio simulado.

| # | Pedido                                      | Tipo                                      | Tempo-alvo |
|---|---------------------------------------------|-------------------------------------------|------------|
| 1 | "2 de 3 veículos disponíveis" na lista      | front: valor calculado (`computed`)       | 10 min     |
| 2 | Atalho diferente por perfil em Meus Dados   | front: `v-if` / `v-else` por perfil       | 10 min     |
| 3 | Tela "Clientes" para o funcionário          | front: tela nova com endpoint que já existe | 15 min   |
| 4 | Manutenção de veículo                       | entidade ligada a outra, com select       | 45–60 min  |

Os quatro foram testados em 18/10/2026 numa cópia do projeto, de três formas: testes do back-end, testes do front-end e uso das telas no navegador.

Para treinar, faça numa cópia, como no simulado:

```bash
cp -R aproveitamento-ds treino-ocar
cd treino-ocar
```

Depois de cada pedido, rode os testes:

```bash
cd backend && .venv/bin/pytest && cd ..          # back-end
node --test frontend/tests/frontend.test.js      # front-end
```

---

## 1. Contagem de veículos disponíveis

> **Pedido:** "Na lista de veículos, mostre quantos estão disponíveis, por exemplo: *2 de 3 veículos disponíveis*."

**O que você aprende:** `computed`, um valor calculado a partir de outras variáveis. O Vue recalcula sozinho quando a lista muda. É como uma `@property` do Python.

**Passo a passo,** tudo em `frontend/veiculos.html`:

1. **Crie o `computed`.** A página ainda não tem esse bloco, então acrescente-o logo antes do `mounted() {`:
   ```js
   computed: {
     totalDisponiveis() {
       return this.veiculos.filter((v) => v.disponivel).length;
     },
   },
   ```
   - **`this.veiculos`** é a lista que veio da API, a mesma declarada no `data()`.
   - **`.filter((v) => v.disponivel)`** equivale a `[v for v in veiculos if v.disponivel]`.
   - **`.length`** equivale a `len(...)`.
   - **Cuidado com a vírgula** depois da `}` que fecha o `computed`. Sem ela, a tela fica em branco, e o teste do front acusa a linha.
2. **Mostre o valor** logo depois de `<div v-if="modo === 'lista'" class="table-responsive">`:
   ```html
   <p class="text-secondary mb-2">{{ totalDisponiveis }} de {{ veiculos.length }} veículos disponíveis</p>
   ```
   - **No HTML, o `computed` é usado sem parênteses,** como se fosse uma variável.
   - **Como está dentro da lista,** a frase some quando o formulário abre.

**Como conferir:**
- Com 3 veículos cadastrados e 1 alugado, a lista mostra "2 de 3 veículos disponíveis".
- Cadastre ou exclua um veículo: o número muda sem apertar F5, porque o `carregar()` atualiza `this.veiculos` e o `computed` é recalculado.

**Testes:** nada a mudar.

---

## 2. Atalho diferente por perfil

> **Pedido:** "Em Meus Dados, mostre um atalho. O funcionário vê um botão para *Veículos*; o cliente, um botão para *Minhas Locações*."

**O que você aprende:** mostrar conteúdo diferente conforme o perfil, com `v-if` / `v-else` e o `usuarioLogado`.

**Passo a passo:** em `frontend/meusdados.html`, acrescente este bloco logo **antes** da linha `<div class="text-end mt-3" v-if="!alterandoSenha">`:

```html
<div class="mt-3">
  <a v-if="usuarioLogado.perfil === 'FUNCIONARIO'" href="veiculos.html" class="btn btn-outline-secondary">
    <i class="bi bi-car-front"></i> Ir para Veículos
  </a>
  <a v-else href="minhaslocacoes.html" class="btn btn-outline-secondary">
    <i class="bi bi-calendar-check"></i> Ir para Minhas Locações
  </a>
</div>
```

- **`usuarioLogado`** existe em todas as telas protegidas. O `criarApp`, em `js/app.js`, lê do token o `id`, o `login` e o `perfil`. No `<script>`, ele é acessado como `this.usuarioLogado.perfil`.
- **`v-if` / `v-else`** funcionam como o `if` / `else` do Python. O `v-else` precisa vir **logo depois** do elemento que tem o `v-if`, sem nada entre os dois.
- **Por que antes daquela linha:** o `<div ... v-if="!alterandoSenha">` e o `<form v-else>` logo abaixo dele formam outro par `v-if` / `v-else`. Colocar algo entre os dois quebraria esse par.
- **Os ícones** (`bi bi-...`) são da Bootstrap Icons, os mesmos do menu.
- **Esconder no front não é segurança.** Se o cliente digitar `veiculos.html` na barra, a própria tela o manda de volta ao menu, por causa do `perfis: ['FUNCIONARIO']`, e a API responde 403.

**Variação:** se só o funcionário deve ver o atalho, apague o `<a v-else ...>` inteiro, até o `</a>`.

**Como conferir:** logado como funcionário, aparece "Ir para Veículos"; como cliente, "Ir para Minhas Locações". Cada botão abre a tela certa.

**Testes:** nada a mudar.

---

## 3. Tela "Clientes"

> **Pedido:** "Crie a tela *Clientes*, só para o funcionário, com o código e o login dos clientes cadastrados. Ela fica no menu do funcionário."

**O que você aprende:** criar uma tela nova a partir de outra parecida, usando um endpoint que já existe. O back-end **não muda**: o `GET /usuarios/clientes` já existe, só o funcionário acessa, e é ele que alimenta o select de clientes em Gerenciar Locações. Para ver o que ele devolve, teste no Swagger (http://localhost:8080/docs): é uma lista como `[{"id": 1, "login": "maria", "perfil": "CLIENTE"}]`.

**Passo a passo:**

1. **Copie a tela mais parecida.** A `minhaslocacoes.html` serve: é só leitura, sem formulário.
   ```bash
   cp frontend/minhaslocacoes.html frontend/clientes.html
   ```
2. **Adapte o `frontend/clientes.html`:**
   - **`<title>` e `<h1>`:** "Clientes".
   - **Tabela:** colunas Código e Login, com um `v-for` sobre `clientes`.
   - **Script:** `perfis: ['FUNCIONARIO']`, `clientes: []` no `data()` e o `mounted` buscando `/usuarios/clientes`. Ele fica mais simples que o da cópia, porque a API já devolve tudo o que a tabela mostra.

   <details>
   <summary>Arquivo completo</summary>

   ```html
   <!DOCTYPE html>
   <html lang="pt-BR">
   <head>
     <meta charset="UTF-8">
     <meta name="viewport" content="width=device-width, initial-scale=1">
     <title>OCar - Clientes</title>
     <link rel="stylesheet" href="vendor/bootstrap/bootstrap.min.css">
     <link rel="stylesheet" href="vendor/bootstrap-icons/bootstrap-icons.min.css">
     <link rel="stylesheet" href="css/style.css">
   </head>
   <body class="bg-light">
   <div id="app" v-cloak class="d-flex flex-column min-vh-100">
     <app-header></app-header>

     <main class="container py-4 flex-grow-1">
       <h1 class="h4 mb-3">Clientes</h1>

       <div v-if="erro" class="alert alert-danger">{{ erro }}</div>

       <div class="table-responsive">
         <table class="table table-striped bg-white border">
           <thead class="table-light">
             <tr>
               <th>Código</th>
               <th>Login</th>
             </tr>
           </thead>
           <tbody>
             <tr v-for="cliente in clientes" :key="cliente.id">
               <td>{{ cliente.id }}</td>
               <td>{{ cliente.login }}</td>
             </tr>
             <tr v-if="clientes.length === 0">
               <td colspan="2" class="text-center text-secondary">Nenhum cliente cadastrado.</td>
             </tr>
           </tbody>
         </table>
       </div>
     </main>

     <app-footer></app-footer>
   </div>

   <script src="vendor/vue.global.js"></script>
   <script src="js/auth.js"></script>
   <script src="js/api.js"></script>
   <script src="js/app.js"></script>
   <script>
     criarApp({
       perfis: ['FUNCIONARIO'],
       data() {
         return {
           clientes: [],
           erro: '',
         };
       },
       async mounted() {
         try {
           this.clientes = await api.get('/usuarios/clientes');
         } catch (e) {
           this.erro = e.message;
         }
       },
     }).mount('#app');
   </script>
   </body>
   </html>
   ```
   </details>
3. **Menu:** em `frontend/menu.html`, acrescente uma linha na lista `itens`. A ordem das linhas é a ordem dos cards.
   ```js
   { titulo: 'Clientes', icone: 'bi-people', url: 'clientes.html', perfis: ['FUNCIONARIO'] },
   ```
4. **Testes do front,** em `frontend/tests/frontend.test.js`:
   - em `PERFIS`, a tela nova:
     ```js
     'clientes.html': ["'FUNCIONARIO'"],
     ```
   - no teste "menu: cada perfil vê...", a lista do funcionário, em ordem alfabética:
     ```js
     assert.deepEqual(para('FUNCIONARIO'), ['Clientes', 'Gerenciar Locações', 'Meus Dados', 'Veículos']);
     ```

**Como conferir:**
- **Como funcionário:** o card "Clientes" aparece no menu, e a tela lista só os clientes, sem os funcionários.
- **Como cliente:** o card não aparece. Digitando `clientes.html` na barra, você volta para o menu.

---

## 4. Manutenção de veículo

> **Pedido:** "O funcionário registra manutenções: escolhe o veículo num select e informa a descrição. A tela lista as manutenções com a placa do veículo."
>
> Continuação comum: "Veículo com manutenção não pode ser excluído." Ela está no passo 10.

**O que você aprende:** criar uma entidade que aponta para outra, com chave estrangeira, e um select no formulário. O modelo pronto no projeto é a `Locacao`: o `veiculo_id` com o `relationship()` em `entities/locacao.py`, e o select com a placa em `gerenciarlocacoes.html`. É a receita 3.8 do guia, aqui completa.

### Back-end

A ordem segue as camadas: entity → DTO → repository → service → controller → `main.py`.

1. **Entity:** crie `backend/app/entities/manutencao.py`.
   ```python
   from sqlalchemy import ForeignKey, String
   from sqlalchemy.orm import Mapped, mapped_column, relationship

   from app.database import Base
   from app.entities.veiculo import Veiculo


   class Manutencao(Base):
       __tablename__ = "manutencao"

       id: Mapped[int] = mapped_column(primary_key=True)
       descricao: Mapped[str] = mapped_column(String(255))
       veiculo_id: Mapped[int] = mapped_column(ForeignKey("veiculo.id"))
       veiculo: Mapped[Veiculo] = relationship()
   ```
   - **`veiculo_id`** é a coluna da chave estrangeira. O `"veiculo.id"` é o `__tablename__` do `Veiculo` mais a coluna `id`.
   - **`relationship()`** permite escrever `manutencao.veiculo` e receber o objeto inteiro. Os dois juntos equivalem ao `@ManyToOne` / `@JoinColumn` do JPA.
2. **Registro da entity:** no fim de `backend/app/entities/__init__.py`, acrescente a linha abaixo. Sem ela, a tabela não é criada, e o erro é `no such table`.
   ```python
   from app.entities.manutencao import Manutencao
   ```
3. **DTO:** crie `backend/app/dtos/manutencao_dto.py`. O front manda e recebe só o id do veículo, em camelCase, como no `LocacaoRequestDTO`.
   ```python
   from pydantic import BaseModel, Field

   from app.dtos.campos import TextoObrigatorio


   class ManutencaoRequestDTO(BaseModel):
       veiculoId: int
       descricao: TextoObrigatorio = Field(max_length=255)


   class ManutencaoResponseDTO(BaseModel):
       id: int
       veiculoId: int
       descricao: str
   ```
4. **Repository:** crie `backend/app/repositories/manutencao_repository.py`. Os métodos `salvar` e `listar` são cópias dos do `veiculo_repository.py`, com os nomes trocados.
   ```python
   from sqlalchemy import select
   from sqlalchemy.orm import Session

   from app.entities.manutencao import Manutencao


   class ManutencaoRepository:
       def __init__(self, db: Session):
           self.db = db

       def salvar(self, manutencao: Manutencao) -> Manutencao:
           self.db.add(manutencao)
           self.db.commit()
           self.db.refresh(manutencao)
           return manutencao

       def listar(self) -> list[Manutencao]:
           return list(self.db.scalars(select(Manutencao).order_by(Manutencao.id)))
   ```
5. **Service:** crie `backend/app/services/manutencao_service.py`.
   ```python
   from sqlalchemy.orm import Session

   from app.dtos.manutencao_dto import ManutencaoRequestDTO, ManutencaoResponseDTO
   from app.entities.manutencao import Manutencao
   from app.exceptions import NaoEncontradoException
   from app.repositories.manutencao_repository import ManutencaoRepository
   from app.repositories.veiculo_repository import VeiculoRepository


   class ManutencaoService:
       def __init__(self, db: Session):
           self.repository = ManutencaoRepository(db)
           self.veiculo_repository = VeiculoRepository(db)

       def listar(self) -> list[ManutencaoResponseDTO]:
           return [self._para_dto(m) for m in self.repository.listar()]

       def cadastrar(self, dto: ManutencaoRequestDTO) -> ManutencaoResponseDTO:
           veiculo = self.veiculo_repository.buscar_por_id(dto.veiculoId)
           if veiculo is None:
               raise NaoEncontradoException("Veículo não encontrado")
           manutencao = Manutencao(veiculo=veiculo, descricao=dto.descricao)
           return self._para_dto(self.repository.salvar(manutencao))

       # A entity tem veiculo_id e o DTO tem veiculoId: por isso a conversão é feita à mão
       def _para_dto(self, manutencao: Manutencao) -> ManutencaoResponseDTO:
           return ManutencaoResponseDTO(id=manutencao.id, veiculoId=manutencao.veiculo_id, descricao=manutencao.descricao)
   ```
   - **Veículo inexistente:** o `cadastrar` confere se o veículo existe e, se não existir, responde 404.
   - **Conversão à mão:** o `_para_dto` monta o DTO manualmente porque os nomes são diferentes: `veiculo_id` na entity e `veiculoId` no DTO. O `model_validate`, usado nos outros services, só copia atributos de mesmo nome.
6. **Controller:** crie `backend/app/controllers/manutencao_controller.py`.
   ```python
   from fastapi import APIRouter, Depends, status
   from sqlalchemy.orm import Session

   from app.database import get_db
   from app.dtos.manutencao_dto import ManutencaoRequestDTO, ManutencaoResponseDTO
   from app.entities.enums import Perfil
   from app.security.dependencias import exigir_perfil
   from app.services.manutencao_service import ManutencaoService

   router = APIRouter(prefix="/manutencoes", tags=["Manutenções"])


   @router.get("", dependencies=[Depends(exigir_perfil(Perfil.FUNCIONARIO))])
   def listar(db: Session = Depends(get_db)) -> list[ManutencaoResponseDTO]:
       return ManutencaoService(db).listar()


   @router.post("", status_code=status.HTTP_201_CREATED, dependencies=[Depends(exigir_perfil(Perfil.FUNCIONARIO))])
   def cadastrar(dto: ManutencaoRequestDTO, db: Session = Depends(get_db)) -> ManutencaoResponseDTO:
       return ManutencaoService(db).cadastrar(dto)
   ```
   - **`prefix`** é o começo da URL de todas as rotas do arquivo.
   - **`exigir_perfil`** faz a rota responder 401 sem token e 403 para cliente.
   - **`status_code=201`** é o padrão do projeto para cadastro.
7. **`backend/app/main.py`:** registre o controller. Sem o `include_router`, as rotas respondem 404.
   ```python
   from app.controllers import autenticacao_controller, locacao_controller, manutencao_controller, usuario_controller, veiculo_controller
   ```
   ```python
   app.include_router(manutencao_controller.router)
   ```
8. **Reinicie o back-end,** se ele não reiniciou sozinho com o `--reload`. Não precisa apagar o `ocar.db`, porque tabela **nova** é criada sozinha. No Swagger, aparece o grupo "Manutenções", com GET e POST.

### Front-end

9. **Tela:** crie `frontend/manutencoes.html`. Ela é uma cópia da `veiculos.html` sem editar e excluir, com quatro pontos novos:
   - **Duas listas no `data()`:** `manutencoes` e `veiculos`. A segunda alimenta o select e a placa da tabela.
   - **`carregar()` busca as duas ao mesmo tempo** com `Promise.all`, como em `gerenciarlocacoes.html`.
   - **`placaVeiculo(id)`** procura a placa pelo id. Equivale a `next((v for v in veiculos if v.id == id), None)` do Python.
   - **O select:** o `<select v-model="form.veiculoId">` guarda o `:value="veiculo.id"` da opção escolhida. O `novo()` começa com `veiculoId: ''` para o select mostrar "Selecione um veículo".

   <details>
   <summary>Arquivo completo</summary>

   ```html
   <!DOCTYPE html>
   <html lang="pt-BR">
   <head>
     <meta charset="UTF-8">
     <meta name="viewport" content="width=device-width, initial-scale=1">
     <title>OCar - Manutenções</title>
     <link rel="stylesheet" href="vendor/bootstrap/bootstrap.min.css">
     <link rel="stylesheet" href="vendor/bootstrap-icons/bootstrap-icons.min.css">
     <link rel="stylesheet" href="css/style.css">
   </head>
   <body class="bg-light">
   <div id="app" v-cloak class="d-flex flex-column min-vh-100">
     <app-header></app-header>

     <main class="container py-4 flex-grow-1">
       <div class="d-flex justify-content-between align-items-center mb-3">
         <h1 class="h4 mb-0">Manutenções</h1>
         <button v-if="modo === 'lista'" class="btn btn-primary" @click="novo">
           <i class="bi bi-plus-lg"></i> Cadastrar
         </button>
       </div>

       <div v-if="erro" class="alert alert-danger">{{ erro }}</div>
       <div v-if="sucesso" class="alert alert-success">{{ sucesso }}</div>

       <!-- Lista -->
       <div v-if="modo === 'lista'" class="table-responsive">
         <table class="table table-striped table-hover bg-white border">
           <thead class="table-light">
             <tr>
               <th>Veículo</th>
               <th>Descrição</th>
             </tr>
           </thead>
           <tbody>
             <tr v-for="manutencao in manutencoes" :key="manutencao.id">
               <td class="text-nowrap">{{ placaVeiculo(manutencao.veiculoId) }}</td>
               <td>{{ manutencao.descricao }}</td>
             </tr>
             <tr v-if="manutencoes.length === 0">
               <td colspan="2" class="text-center text-secondary">Nenhuma manutenção cadastrada.</td>
             </tr>
           </tbody>
         </table>
       </div>

       <!-- Formulário (cadastro) -->
       <form v-else class="card card-body" @submit.prevent="salvar">
         <div class="row g-3">
           <div class="col-12 col-md-6">
             <label class="form-label" for="veiculo">Veículo</label>
             <select id="veiculo" class="form-select" v-model="form.veiculoId" required>
               <option value="" disabled>Selecione um veículo</option>
               <option v-for="veiculo in veiculos" :key="veiculo.id" :value="veiculo.id">
                 {{ veiculo.descricao }} - {{ veiculo.placa }}
               </option>
             </select>
           </div>
           <div class="col-12 col-md-6">
             <label class="form-label" for="descricao">Descrição</label>
             <input id="descricao" class="form-control" v-model.trim="form.descricao" required>
           </div>
         </div>
         <div class="d-flex justify-content-end gap-2 mt-4">
           <button type="button" class="btn btn-outline-secondary" @click="voltar">Voltar</button>
           <button type="submit" class="btn btn-primary">Salvar</button>
         </div>
       </form>
     </main>

     <app-footer></app-footer>
   </div>

   <script src="vendor/vue.global.js"></script>
   <script src="js/auth.js"></script>
   <script src="js/api.js"></script>
   <script src="js/app.js"></script>
   <script>
     criarApp({
       perfis: ['FUNCIONARIO'],
       data() {
         return {
           manutencoes: [],
           veiculos: [],
           modo: 'lista', // 'lista' ou 'form'
           form: {},
           erro: '',
           sucesso: '',
         };
       },
       mounted() {
         this.carregar();
       },
       methods: {
         async carregar() {
           try {
             // Busca as duas listas ao mesmo tempo
             [this.manutencoes, this.veiculos] = await Promise.all([
               api.get('/manutencoes'),
               api.get('/veiculos'),
             ]);
           } catch (e) {
             this.erro = e.message;
           }
         },
         // A API devolve só o veiculoId; a placa vem da lista de veículos
         placaVeiculo(id) {
           const veiculo = this.veiculos.find((v) => v.id === id);
           return veiculo ? veiculo.placa : `#${id}`;
         },
         limparMensagens() {
           this.erro = '';
           this.sucesso = '';
         },
         novo() {
           this.limparMensagens();
           this.form = { veiculoId: '', descricao: '' };
           this.modo = 'form';
         },
         voltar() {
           this.limparMensagens();
           this.modo = 'lista';
         },
         async salvar() {
           this.limparMensagens();
           try {
             await api.post('/manutencoes', { veiculoId: this.form.veiculoId, descricao: this.form.descricao });
             this.sucesso = 'Manutenção cadastrada com sucesso.';
             this.modo = 'lista';
             await this.carregar();
           } catch (e) {
             this.erro = e.message;
           }
         },
       },
     }).mount('#app');
   </script>
   </body>
   </html>
   ```
   </details>

   E uma linha na lista `itens` de `frontend/menu.html`:
   ```js
   { titulo: 'Manutenções', icone: 'bi-tools', url: 'manutencoes.html', perfis: ['FUNCIONARIO'] },
   ```

### Testes

- **Back-end:** crie `backend/tests/test_manutencoes.py`.
  ```python
  def test_cadastrar_e_listar(client, api, funcionario):
      veiculo = api.veiculo(funcionario.headers)
      corpo = {"veiculoId": veiculo["id"], "descricao": "Troca de óleo"}
      r = client.post("/manutencoes", json=corpo, headers=funcionario.headers)
      assert r.status_code == 201
      manutencao = r.json()
      assert manutencao == {"id": 1, "veiculoId": veiculo["id"], "descricao": "Troca de óleo"}

      assert client.get("/manutencoes", headers=funcionario.headers).json() == [manutencao]


  def test_veiculo_inexistente(client, funcionario):
      r = client.post("/manutencoes", json={"veiculoId": 99, "descricao": "Troca de óleo"}, headers=funcionario.headers)
      assert r.status_code == 404
      assert r.json() == {"detail": "Veículo não encontrado"}


  def test_so_funcionario_acessa(client, cliente):
      assert client.get("/manutencoes").status_code == 401
      assert client.get("/manutencoes", headers=cliente.headers).status_code == 403
  ```
- **Front-end,** em `frontend/tests/frontend.test.js`:
  - em `PERFIS`:
    ```js
    'manutencoes.html': ["'FUNCIONARIO'"],
    ```
  - no teste "menu: cada perfil vê...", a lista do funcionário em ordem alfabética: `['Gerenciar Locações', 'Manutenções', 'Meus Dados', 'Veículos']`. Se você também fez a tela Clientes:
    ```js
    assert.deepEqual(para('FUNCIONARIO'), ['Clientes', 'Gerenciar Locações', 'Manutenções', 'Meus Dados', 'Veículos']);
    ```

### Se o professor pedir: veículo com manutenção não pode ser excluído

10. **Siga a mesma ideia da R09** ("veículo com locação não pode ser excluído"). O banco não impede a exclusão sozinho, porque o SQLite não confere chave estrangeira por padrão. Sem a regra, a manutenção ficaria apontando para um veículo apagado e apareceria como `#2` na lista.
    - Em `backend/app/repositories/manutencao_repository.py`, um método novo:
      ```python
      def existe_por_veiculo(self, veiculo_id: int) -> bool:
          return self.db.scalar(select(Manutencao.id).where(Manutencao.veiculo_id == veiculo_id).limit(1)) is not None
      ```
    - Em `backend/app/services/veiculo_service.py`, em três lugares:
      - nos imports:
        ```python
        from app.repositories.manutencao_repository import ManutencaoRepository
        ```
      - no `__init__`:
        ```python
        self.manutencao_repository = ManutencaoRepository(db)
        ```
      - no `excluir`, logo depois da checagem da R09:
        ```python
        # Nova regra: veículo com manutenção também não pode ser excluído
        if self.manutencao_repository.existe_por_veiculo(id):
            raise ConflitoException("Veículo com manutenções não pode ser excluído")
        ```
    - Teste, no fim de `backend/tests/test_manutencoes.py`:
      ```python
      def test_veiculo_com_manutencao_nao_pode_ser_excluido(client, api, funcionario):
          veiculo = api.veiculo(funcionario.headers)
          client.post("/manutencoes", json={"veiculoId": veiculo["id"], "descricao": "Troca de óleo"}, headers=funcionario.headers)
          r = client.delete(f"/veiculos/{veiculo['id']}", headers=funcionario.headers)
          assert r.status_code == 409
          assert r.json() == {"detail": "Veículo com manutenções não pode ser excluído"}
      ```

**Como conferir:**
- Cadastre uma manutenção escolhendo um veículo no select: a lista mostra a placa dele.
- Com o passo 10 feito, tente excluir esse veículo na tela Veículos: aparece o alerta "Veículo com manutenções não pode ser excluído".

---

## Depois dos 4

Com os quatro feitos, todos os testes passam, inclusive o do Insomnia, porque nenhum deles muda o que a coleção da Parte I envia. Se algo falhar numa parte em que você não mexeu, veja a seção 5 do `guia-alteracoes.md`, "Quando algo dá errado".
