# Guia de alterações

Para quem sabe Python e não conhece Vue. Cada receita diz **em qual arquivo mexer** e traz o código pronto para copiar.

As receitas foram aplicadas numa cópia do projeto e conferidas com os testes automáticos e no navegador.

1. [Mapa rápido: quero X → mexo em Y](#1-mapa-rápido)
2. [Como uma página funciona (Vue para quem sabe Python)](#2-como-uma-página-funciona)
3. Receitas
   - [3.1 Texto, cor, ícone e layout](#31-texto-cor-ícone-e-layout)
   - [3.2 Mostrar algo só para um perfil](#32-mostrar-algo-só-para-um-perfil)
   - [3.3 Campo novo numa entidade que já existe](#33-campo-novo-numa-entidade-que-já-existe-ex-cor-no-veículo)
   - [3.4 Tipos de campo (data, número, sim/não, lista fixa, opcional)](#34-tipos-de-campo)
   - [3.5 Busca numa lista](#35-busca-numa-lista)
   - [3.6 Formatar um valor na tela](#36-formatar-um-valor-na-tela)
   - [3.7 Entidade nova com tela de cadastro](#37-entidade-nova-com-tela-de-cadastro-ex-filial)
   - [3.8 Entidade que aponta para outra (select)](#38-entidade-que-aponta-para-outra-ex-manutenção-de-um-veículo)
   - [3.9 Regra de negócio nova](#39-regra-de-negócio-nova)
   - [3.10 Mudar quem pode acessar](#310-mudar-quem-pode-acessar)
4. [Depois de cada mudança](#4-depois-de-cada-mudança)
5. [Quando algo dá errado](#5-quando-algo-dá-errado)

---

## 1. Mapa rápido

| Quero...                                       | Mexo em                                                                         |
|------------------------------------------------|---------------------------------------------------------------------------------|
| Mudar texto, título ou botão de uma tela       | o `.html` da tela, em `frontend/`                                               |
| Mudar o cabeçalho ou o rodapé de todas as telas| `frontend/js/app.js` (`AppHeader`, `AppFooter`)                                 |
| Mudar estilo de todas as telas                 | `frontend/css/style.css`                                                        |
| Item novo no menu                              | `frontend/menu.html`, lista `itens`                                             |
| Coluna nova numa tabela / campo num formulário | o `.html` da tela + back-end ([3.3](#33-campo-novo-numa-entidade-que-já-existe-ex-cor-no-veículo)) |
| Tela nova                                      | `frontend/<nova>.html` + menu ([3.7](#37-entidade-nova-com-tela-de-cadastro-ex-filial)) |
| Traduzir um enum ou formatar valor/data        | `fmt` em `frontend/js/app.js` ([3.6](#36-formatar-um-valor-na-tela))            |
| Regra de negócio                               | `backend/app/services/<x>_service.py` ([3.9](#39-regra-de-negócio-nova))        |
| Endpoint novo                                  | controller → service → repository                                               |
| Quem pode acessar                              | controller + `perfis` da página + menu ([3.10](#310-mudar-quem-pode-acessar))   |

Caminho de uma requisição: **página `.html`** → `api.js` → **controller** → **service** (regras) → **repository** → banco.

---

## 2. Como uma página funciona

Cada tela é **um arquivo `.html`** em `frontend/`, com duas partes: o HTML em cima e o `<script>` embaixo.
O resumo de `veiculos.html`:

```html
<div id="app" v-cloak ...>                     ← tudo que o Vue controla fica aqui dentro
  <app-header></app-header>                    ← cabeçalho (definido em js/app.js)
  <main class="container ...">
    <h1>Veículos</h1>
    <div v-if="erro" class="alert alert-danger">{{ erro }}</div>     ← mensagens
    <div v-if="modo === 'lista'"> <table>...</table> </div>          ← modo lista
    <form v-else @submit.prevent="salvar"> ... </form>               ← modo formulário
  </main>
  <app-footer></app-footer>                    ← rodapé "Funcionário: jose"
</div>

<script src="vendor/vue.global.js"></script>   ← não mexa: bibliotecas, nesta ordem
<script src="js/auth.js"></script>
<script src="js/api.js"></script>
<script src="js/app.js"></script>
<script>
  criarApp({
    perfis: ['FUNCIONARIO'],                   ← quem pode abrir a tela
    data() { return { veiculos: [], modo: 'lista', form: {}, erro: '', sucesso: '' }; },  ← variáveis
    mounted() { this.carregar(); },            ← roda quando a tela abre
    methods: { carregar() {...}, salvar() {...} },                    ← funções
  }).mount('#app');
</script>
```

**A ideia central:** você muda a variável e o Vue redesenha a tela sozinho.
- **Ao abrir a tela:** o `mounted()` chama `carregar()`, que faz `this.veiculos = await api.get('/veiculos')`, e a tabela aparece.
- **Para trocar entre lista e formulário:** basta `this.modo = 'form'`.
- Nunca use `document.getElementById(...)` para mudar a tela.

### No HTML

| Escrevo                               | Significa                                                     | Em Python seria                 |
|---------------------------------------|---------------------------------------------------------------|---------------------------------|
| `{{ veiculo.placa }}`                 | mostra o valor                                                | `f"{veiculo.placa}"`            |
| `v-for="veiculo in veiculos"`         | repete o elemento para cada item (exige `:key="veiculo.id"`)  | `for veiculo in veiculos:`      |
| `v-if="modo === 'lista'"` / `v-else`  | só mostra se for verdade                                      | `if ... else`                   |
| `v-model.trim="form.placa"`           | liga o input à variável, nos dois sentidos; `.trim` tira espaços | —                            |
| `v-model.number="form.idade"`         | igual, mas converte para número                               | `int(...)`                      |
| `@click="editar(veiculo)"`            | chama o método ao clicar                                      | `on_click=editar`               |
| `@submit.prevent="salvar"`            | chama `salvar` ao enviar o form, sem recarregar a página      | —                               |
| `:disabled="!!form.id"`               | `:` na frente = o valor é uma expressão, não texto            | —                               |

### No `<script>`

| Parte              | Para que serve                                                    | Em Python seria         |
|--------------------|-------------------------------------------------------------------|-------------------------|
| `perfis: [...]`    | quem pode abrir a tela (outro perfil volta para o menu)           | —                       |
| `data()`           | as variáveis da tela, com o valor inicial                         | atributos no `__init__` |
| `mounted()`        | roda uma vez, quando a tela abre                                  | —                       |
| `methods`          | funções da tela                                                   | métodos                 |
| `computed`         | valor calculado a partir de outras variáveis, recalculado sozinho | `@property`             |
| `this.veiculos`    | acessa uma variável ou método **dentro do script**                | `self.veiculos`         |

### JavaScript para quem sabe Python

| Python                         | JavaScript                                                      |
|--------------------------------|-----------------------------------------------------------------|
| `True / False / None`          | `true / false / null`                                           |
| `==`, `and`, `or`, `not`       | `===`, `&&`, `\|\|`, `!`                                        |
| `f"/veiculos/{id}"`            | `` `/veiculos/${id}` `` (crase)                                 |
| `len(lista)`                   | `lista.length`                                                  |
| `[v for v in lista if v.ok]`   | `lista.filter((v) => v.ok)`                                     |
| `[v.placa for v in lista]`     | `lista.map((v) => v.placa)`                                     |
| `next(v for v in l if v.id == 1)` | `l.find((v) => v.id === 1)`                                  |
| `dict(veiculo)` (cópia)        | `{ ...veiculo }`                                                |
| `try/except Exception as e`    | `try { } catch (e) { }`                                         |
| `requests.get(url).json()`     | `await api.get(url)` (dentro de um método `async`)              |

### Pegadinhas

- **`this`:** no HTML não se usa `this` (`{{ veiculo.placa }}`); no script, sim (`this.veiculos`).
- **Vírgulas:** os itens de `data()` e de `methods` são separados por **vírgula**. Esquecer uma quebra a página inteira: ela fica em branco ou mostra `{{ }}`.
- **Variáveis:** toda variável usada no HTML precisa existir no `data()`, no `computed` ou nos `methods`.
- **Nomes dos campos:** o corpo enviado em `api.post` precisa ter os **mesmos nomes do RequestDTO** (ex.: `veiculoId`, não `veiculo_id`).
- **`api.js`:** tem `api.get`, `api.post`, `api.patch` e `api.delete`, sem `put`. O token vai sozinho, e em erro o `e.message` já traz a mensagem do back-end.

---

## 3. Receitas

### 3.1 Texto, cor, ícone e layout

- **Texto:** abra o `.html` da tela, procure o texto (Cmd+F) e troque.
- **Cor de botão:** troque a classe do Bootstrap.
  - `btn-primary` (azul), `btn-success` (verde), `btn-danger` (vermelho), `btn-warning` (amarelo), `btn-secondary` (cinza).
  - `btn-outline-...` deixa só a borda.
- **Cor de texto e fundo:** `text-danger`, `text-success`, `text-secondary`, `fw-bold`, `bg-light`, `bg-white`.
- **Ícone:** `<i class="bi bi-car-front"></i>`. Para listar os nomes sem internet:
  ```bash
  grep -o 'bi-[a-z0-9-]*' frontend/vendor/bootstrap-icons/bootstrap-icons.min.css | sort -u | grep car
  ```
- **Lado a lado no computador e empilhado no celular:** `<div class="row">` com filhos `<div class="col-12 col-md-6">`.
- **Todas as telas:** estilos em `frontend/css/style.css`; cabeçalho e rodapé em `frontend/js/app.js`.

### 3.2 Mostrar algo só para um perfil

Em qualquer tela, no HTML:

```html
<div v-if="usuarioLogado.perfil === 'FUNCIONARIO'" class="alert alert-info">Só funcionário vê isto</div>
```

- **No script:** use `this.usuarioLogado.perfil`, `this.usuarioLogado.login` e `this.usuarioLogado.id`.
- **Atenção:** esconder no front **não protege a API**. Proteja também no controller ([3.10](#310-mudar-quem-pode-acessar)).

### 3.3 Campo novo numa entidade que já existe (ex.: `cor` no veículo)

**Back-end:**

1. `backend/app/entities/veiculo.py`: no fim da classe:
   ```python
   cor: Mapped[str] = mapped_column(String(30))
   ```
2. `backend/app/dtos/veiculo_dto.py`: no `VeiculoRequestDTO` e no `VeiculoResponseDTO`:
   ```python
   class VeiculoRequestDTO(BaseModel):
       ...
       cor: TextoObrigatorio = Field(max_length=30)

   class VeiculoResponseDTO(BaseModel):
       ...
       cor: str
   ```
3. `backend/app/services/veiculo_service.py`, no `cadastrar`:
   ```python
   veiculo = Veiculo(placa=dto.placa, descricao=dto.descricao, disponivel=True, cor=dto.cor)
   ```
4. **Apague `backend/ocar.db`** e reinicie o back-end. A tabela é recriada com a coluna nova.

**Front-end:** `frontend/veiculos.html`, em 5 lugares:

1. Cabeçalho da tabela, depois de `<th>Placa</th>`:
   ```html
   <th>Cor</th>
   ```
2. Linha da tabela, na mesma posição, depois do `<td>` da placa:
   ```html
   <td>{{ veiculo.cor }}</td>
   ```
   Na linha "Nenhum veículo cadastrado", troque `colspan="4"` por `colspan="5"`, porque agora são 5 colunas.
3. Formulário: um bloco novo depois do bloco da placa:
   ```html
   <div class="col-12 col-md-6">
     <label class="form-label" for="cor">Cor</label>
     <input id="cor" class="form-control" v-model.trim="form.cor" :disabled="!!form.id" required>
   </div>
   ```
   O `:disabled="!!form.id"` bloqueia o campo na edição. Tire-o se a cor puder ser alterada; nesse caso, inclua `cor` também no `VeiculoDescricaoRequestDTO`, no `alterar_descricao` do service e no `api.patch` do `salvar()`.
4. No `novo()`, valor inicial:
   ```js
   this.form = { id: null, descricao: '', placa: '', disponivel: true, cor: '' };
   ```
5. No `salvar()`, envie o campo:
   ```js
   await api.post('/veiculos', { placa: this.form.placa, descricao: this.form.descricao, cor: this.form.cor });
   ```

**Testes:**
- `backend/tests/dados.py`: `"cor": "Prata"` no `corpo_veiculo`.
- `backend/tests/test_modelo.py`: `"cor"` nas três listas do Veiculo (entidade, `VeiculoRequestDTO` e `VeiculoResponseDTO`).

Depois disso, só o `test_insomnia.py` falha. É esperado, porque a coleção da Parte I não envia `cor`.

### 3.4 Tipos de campo

Testado com a API e no navegador: cada tipo grava e volta certo, e valores inválidos dão 422.

| Tipo                  | Entity (`entities/`)                                                       | DTO (`dtos/`)                                 | Input no HTML                                                                         |
|-----------------------|----------------------------------------------------------------------------|-----------------------------------------------|---------------------------------------------------------------------------------------|
| Texto                 | `nome: Mapped[str] = mapped_column(String(100))`                            | `nome: TextoObrigatorio = Field(max_length=100)` | `<input class="form-control" v-model.trim="form.nome" required>`                    |
| Inteiro               | `quantidade: Mapped[int]`                                                   | `quantidade: int = Field(ge=0)`               | `<input type="number" class="form-control" v-model.number="form.quantidade" required>` |
| Valor (decimal)       | `valor: Mapped[float]`                                                      | `valor: float = Field(gt=0)`                  | `<input type="number" step="0.01" class="form-control" v-model.number="form.valor" required>` |
| Data                  | `data: Mapped[date]` (+ `from datetime import date`)                        | `data: date` (+ `from datetime import date`)  | `<input type="date" class="form-control" v-model="form.data" required>`               |
| Sim/Não               | `ativo: Mapped[bool] = mapped_column(default=True)`                         | `ativo: bool`                                 | `<input type="checkbox" class="form-check-input" v-model="form.ativo">`               |
| Lista fixa (enum)     | `categoria: Mapped[Categoria] = mapped_column(Enum(Categoria, native_enum=False, length=20))` | `categoria: Categoria`                       | `<select>` (abaixo)                                                                   |
| Opcional              | `obs: Mapped[str \| None] = mapped_column(String(255))`                     | `obs: str \| None = Field(default=None, max_length=255)` | input **sem** `required`                                                    |

- **Data:** o input `type="date"` já manda no formato `2026-10-23`, que é o que a API espera.
- **Sim/Não no formulário:** use o modelo abaixo.
  ```html
  <div class="form-check">
    <input id="ativo" type="checkbox" class="form-check-input" v-model="form.ativo">
    <label class="form-check-label" for="ativo">Ativo</label>
  </div>
  ```
- **Lista fixa (enum):**
  1. Crie a classe em `backend/app/entities/enums.py`, como `Situacao`:
     ```python
     class Categoria(StrEnum):
         PEQUENA = "PEQUENA"
         GRANDE = "GRANDE"
     ```
  2. Importe com `from app.entities.enums import Categoria` na entity e no DTO (`Enum` vem de `sqlalchemy`).
  3. No HTML:
     ```html
     <select id="categoria" class="form-select" v-model="form.categoria" required>
       <option value="" disabled>Selecione</option>
       <option value="PEQUENA">Pequena</option>
       <option value="GRANDE">Grande</option>
     </select>
     ```
  4. Na tabela, mostre com `{{ fmt.categoria(item.categoria) }}` ([3.6](#36-formatar-um-valor-na-tela)).
- **Campo opcional:**
  - No `salvar()`, envie `obs: this.form.obs || null`, para o campo vazio ser gravado como `null` e não como `""`.
  - O `test_modelo.py` exige NOT NULL nas tabelas do enunciado. Se colocar um opcional em `usuario`, `veiculo` ou `locacao`, esse teste falha; ajuste-o.
- **Número no formulário:** com `v-model.number`, o valor vai para a API como número. Na edição, o `{ ...item }` já preenche o input.

### 3.5 Busca numa lista

Exemplo em `frontend/veiculos.html`:

1. No `data()`, adicione a variável:
   ```js
   busca: '',
   ```
2. Antes do `mounted()`, adicione o `computed`:
   ```js
   computed: {
     veiculosFiltrados() {
       const termo = this.busca.toLowerCase();
       return this.veiculos.filter((v) => (v.placa + ' ' + v.descricao).toLowerCase().includes(termo));
     },
   },
   ```
3. Logo depois de `<div v-if="modo === 'lista'" class="table-responsive">`:
   ```html
   <input class="form-control mb-3" v-model.trim="busca" placeholder="Buscar por placa ou descrição">
   ```
4. Troque `veiculos` por `veiculosFiltrados` em dois lugares:
   - `v-for="veiculo in veiculosFiltrados"`
   - `v-if="veiculosFiltrados.length === 0"`

Para filtrar por um select (ex.: só disponíveis), a ideia é a mesma: `.filter((v) => v.disponivel)` no `computed`.

### 3.6 Formatar um valor na tela

Os formatadores ficam no objeto `fmt`, no topo de `frontend/js/app.js`, e valem para todas as telas.
Para criar um, adicione uma linha:

```js
const fmt = {
  ...
  moeda: (valor) => Number(valor).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }),  // R$ 1.500,50
  data: (valor) => valor.split('-').reverse().join('/'),                                           // 23/10/2026
  categoria: (valor) => ({ PEQUENA: 'Pequena', GRANDE: 'Grande' })[valor] || valor,
};
```

Para usar na tela: `{{ fmt.moeda(filial.aluguel) }}`.

### 3.7 Entidade nova com tela de cadastro (ex.: Filial)

Este exemplo cria um CRUD completo de `Filial(id, nome, cidade)`, só para FUNCIONARIO: listar, cadastrar, alterar e excluir.
Para outra entidade, copie e troque `Filial`/`filial`/`filiais` pelo nome novo, e `nome`/`cidade` pelos campos.

**Back-end:** 5 arquivos novos e 2 alterados.

<details>
<summary><code>backend/app/entities/filial.py</code> (novo)</summary>

```python
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Filial(Base):
    __tablename__ = "filial"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100))
    cidade: Mapped[str] = mapped_column(String(100))
```
</details>

`backend/app/entities/__init__.py`: adicione no fim a linha abaixo. Sem ela, a tabela não é criada.

```python
from app.entities.filial import Filial
```

<details>
<summary><code>backend/app/dtos/filial_dto.py</code> (novo)</summary>

```python
from pydantic import BaseModel, ConfigDict, Field

from app.dtos.campos import TextoObrigatorio


class FilialRequestDTO(BaseModel):
    nome: TextoObrigatorio = Field(max_length=100)
    cidade: TextoObrigatorio = Field(max_length=100)


class FilialResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    cidade: str
```
</details>

<details>
<summary><code>backend/app/repositories/filial_repository.py</code> (novo)</summary>

```python
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.entities.filial import Filial


class FilialRepository:
    def __init__(self, db: Session):
        self.db = db

    def salvar(self, filial: Filial) -> Filial:
        self.db.add(filial)
        self.db.commit()
        self.db.refresh(filial)
        return filial

    def excluir(self, filial: Filial) -> None:
        self.db.delete(filial)
        self.db.commit()

    def buscar_por_id(self, id: int) -> Filial | None:
        return self.db.get(Filial, id)

    def listar(self) -> list[Filial]:
        return list(self.db.scalars(select(Filial).order_by(Filial.id)))
```
</details>

<details>
<summary><code>backend/app/services/filial_service.py</code> (novo)</summary>

```python
from sqlalchemy.orm import Session

from app.dtos.filial_dto import FilialRequestDTO, FilialResponseDTO
from app.entities.filial import Filial
from app.exceptions import NaoEncontradoException
from app.repositories.filial_repository import FilialRepository


class FilialService:
    def __init__(self, db: Session):
        self.repository = FilialRepository(db)

    def listar(self) -> list[FilialResponseDTO]:
        return [FilialResponseDTO.model_validate(f) for f in self.repository.listar()]

    def buscar(self, id: int) -> FilialResponseDTO:
        return FilialResponseDTO.model_validate(self._buscar_entidade(id))

    def cadastrar(self, dto: FilialRequestDTO) -> FilialResponseDTO:
        filial = Filial(nome=dto.nome, cidade=dto.cidade)
        return FilialResponseDTO.model_validate(self.repository.salvar(filial))

    def alterar(self, id: int, dto: FilialRequestDTO) -> FilialResponseDTO:
        filial = self._buscar_entidade(id)
        filial.nome = dto.nome
        filial.cidade = dto.cidade
        return FilialResponseDTO.model_validate(self.repository.salvar(filial))

    def excluir(self, id: int) -> None:
        self.repository.excluir(self._buscar_entidade(id))

    def _buscar_entidade(self, id: int) -> Filial:
        filial = self.repository.buscar_por_id(id)
        if filial is None:
            raise NaoEncontradoException("Filial não encontrada")
        return filial
```
</details>

<details>
<summary><code>backend/app/controllers/filial_controller.py</code> (novo)</summary>

```python
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dtos.filial_dto import FilialRequestDTO, FilialResponseDTO
from app.entities.enums import Perfil
from app.security.dependencias import exigir_perfil
from app.services.filial_service import FilialService

router = APIRouter(prefix="/filiais", tags=["Filiais"])


@router.get("", dependencies=[Depends(exigir_perfil(Perfil.FUNCIONARIO))])
def listar(db: Session = Depends(get_db)) -> list[FilialResponseDTO]:
    return FilialService(db).listar()


@router.get("/{id}", dependencies=[Depends(exigir_perfil(Perfil.FUNCIONARIO))])
def buscar(id: int, db: Session = Depends(get_db)) -> FilialResponseDTO:
    return FilialService(db).buscar(id)


@router.post("", status_code=status.HTTP_201_CREATED, dependencies=[Depends(exigir_perfil(Perfil.FUNCIONARIO))])
def cadastrar(dto: FilialRequestDTO, db: Session = Depends(get_db)) -> FilialResponseDTO:
    return FilialService(db).cadastrar(dto)


@router.patch("/{id}", dependencies=[Depends(exigir_perfil(Perfil.FUNCIONARIO))])
def alterar(id: int, dto: FilialRequestDTO, db: Session = Depends(get_db)) -> FilialResponseDTO:
    return FilialService(db).alterar(id, dto)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(exigir_perfil(Perfil.FUNCIONARIO))])
def excluir(id: int, db: Session = Depends(get_db)) -> None:
    FilialService(db).excluir(id)
```
</details>

`backend/app/main.py`: registre o controller. Sem isso, todas as rotas dão 404.

```python
from app.controllers import autenticacao_controller, filial_controller, locacao_controller, usuario_controller, veiculo_controller
...
app.include_router(filial_controller.router)
```

Reinicie o back-end. Não precisa apagar o `ocar.db`, porque tabela **nova** é criada sozinha. Só tabela **alterada** exige apagar.

**Front-end:** 1 arquivo novo e 1 linha no menu.

`frontend/menu.html`: adicione uma linha na lista `itens`:

```js
{ titulo: 'Filiais', icone: 'bi-building', url: 'filiais.html', perfis: ['FUNCIONARIO'] },
```

<details>
<summary><code>frontend/filiais.html</code> (novo, uma cópia adaptada de <code>veiculos.html</code>)</summary>

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>OCar - Filiais</title>
  <link rel="stylesheet" href="vendor/bootstrap/bootstrap.min.css">
  <link rel="stylesheet" href="vendor/bootstrap-icons/bootstrap-icons.min.css">
  <link rel="stylesheet" href="css/style.css">
</head>
<body class="bg-light">
<div id="app" v-cloak class="d-flex flex-column min-vh-100">
  <app-header></app-header>

  <main class="container py-4 flex-grow-1">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h1 class="h4 mb-0">Filiais</h1>
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
            <th>Nome</th>
            <th>Cidade</th>
            <th class="text-end">Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="filial in filiais" :key="filial.id">
            <td>{{ filial.nome }}</td>
            <td>{{ filial.cidade }}</td>
            <td class="text-end text-nowrap">
              <button class="btn btn-sm btn-outline-primary me-1" @click="editar(filial)" title="Editar">
                <i class="bi bi-pencil"></i><span class="d-none d-md-inline"> Editar</span>
              </button>
              <button class="btn btn-sm btn-outline-danger" @click="excluir(filial)" title="Excluir">
                <i class="bi bi-trash"></i><span class="d-none d-md-inline"> Excluir</span>
              </button>
            </td>
          </tr>
          <tr v-if="filiais.length === 0">
            <td colspan="3" class="text-center text-secondary">Nenhuma filial cadastrada.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Formulário (cadastro e edição) -->
    <form v-else class="card card-body" @submit.prevent="salvar">
      <div class="row g-3">
        <div class="col-12 col-md-6">
          <label class="form-label" for="nome">Nome</label>
          <input id="nome" class="form-control" v-model.trim="form.nome" required>
        </div>
        <div class="col-12 col-md-6">
          <label class="form-label" for="cidade">Cidade</label>
          <input id="cidade" class="form-control" v-model.trim="form.cidade" required>
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
        filiais: [],
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
          this.filiais = await api.get('/filiais');
        } catch (e) {
          this.erro = e.message;
        }
      },
      limparMensagens() {
        this.erro = '';
        this.sucesso = '';
      },
      novo() {
        this.limparMensagens();
        this.form = { id: null, nome: '', cidade: '' };
        this.modo = 'form';
      },
      editar(filial) {
        this.limparMensagens();
        this.form = { ...filial };
        this.modo = 'form';
      },
      voltar() {
        this.limparMensagens();
        this.modo = 'lista';
      },
      async salvar() {
        this.limparMensagens();
        const corpo = { nome: this.form.nome, cidade: this.form.cidade };
        try {
          if (this.form.id) {
            await api.patch(`/filiais/${this.form.id}`, corpo);
            this.sucesso = 'Filial alterada com sucesso.';
          } else {
            await api.post('/filiais', corpo);
            this.sucesso = 'Filial cadastrada com sucesso.';
          }
          this.modo = 'lista';
          await this.carregar();
        } catch (e) {
          this.erro = e.message;
        }
      },
      async excluir(filial) {
        if (!confirm(`Excluir a filial ${filial.nome}?`)) return;
        this.limparMensagens();
        try {
          await api.delete(`/filiais/${filial.id}`);
          this.sucesso = 'Filial excluída com sucesso.';
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

O que muda de uma entidade para outra, nesse arquivo:
- **`<title>` e `<h1>`:** o nome da tela.
- **`<th>` e `<td>`:** um par por campo. O `colspan` da linha "Nenhuma..." é igual ao número de colunas.
- **Blocos do formulário:** um `<div class="col-...">` com `label` e `input` por campo.
- **`novo()`:** um campo vazio para cada um.
- **`corpo` no `salvar()`:** os campos com os nomes do RequestDTO.
- **URLs:** troque `'/filiais'` pelo `prefix` do controller.
- **Só listar e cadastrar:** apague os botões Editar/Excluir e os métodos `editar` e `excluir`.

**Testes:**

1. `backend/tests/dados.py`: o corpo padrão:
   ```python
   def corpo_filial(**campos) -> dict:
       return {"nome": "Centro", "cidade": "Joinville", **campos}
   ```
2. `backend/tests/test_filiais.py` (novo):
   ```python
   from dados import corpo_filial


   def test_cadastrar_listar_alterar_excluir(client, funcionario):
       h = funcionario.headers
       r = client.post("/filiais", json=corpo_filial(), headers=h)
       assert r.status_code == 201
       filial = r.json()
       assert filial == {"id": 1, "nome": "Centro", "cidade": "Joinville"}

       assert client.get("/filiais", headers=h).json() == [filial]

       r = client.patch(f"/filiais/{filial['id']}", json=corpo_filial(cidade="Curitiba"), headers=h)
       assert r.json()["cidade"] == "Curitiba"

       assert client.delete(f"/filiais/{filial['id']}", headers=h).status_code == 204
       assert client.get(f"/filiais/{filial['id']}", headers=h).status_code == 404


   def test_campos_obrigatorios(client, funcionario):
       r = client.post("/filiais", json={"nome": "   "}, headers=funcionario.headers)
       assert r.status_code == 422


   def test_so_funcionario_acessa(client, cliente):
       assert client.get("/filiais").status_code == 401
       assert client.get("/filiais", headers=cliente.headers).status_code == 403
   ```
3. `frontend/tests/frontend.test.js`:
   - **Tela nova:** em `PERFIS`, inclua `'filiais.html': ["'FUNCIONARIO'"],`.
   - **Item no menu:** no teste "menu: cada perfil vê...", inclua `'Filiais'` na lista do FUNCIONARIO, em ordem alfabética: `['Filiais', 'Gerenciar Locações', 'Meus Dados', 'Veículos']`.

### 3.8 Entidade que aponta para outra (ex.: manutenção de um veículo)

Neste exemplo, `Manutencao(id, veiculo, descricao)`: o funcionário escolhe o veículo num select.
A estrutura é a mesma da Filial ([3.7](#37-entidade-nova-com-tela-de-cadastro-ex-filial)). Abaixo, só o que é diferente.
O modelo pronto no projeto é a `Locacao`: veja `entities/locacao.py`, `services/locacao_service.py` e `gerenciarlocacoes.html`.

**Entity** `backend/app/entities/manutencao.py`: a chave estrangeira é a coluna `*_id` mais o `relationship()`:

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

**DTO** `backend/app/dtos/manutencao_dto.py`: o front manda e recebe só o id, em camelCase:

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

**Service** `backend/app/services/manutencao_service.py`: o service confere se o veículo existe e monta o DTO à mão, porque a entity tem `veiculo_id` e o DTO tem `veiculoId`:

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

**O resto do back-end** segue a Filial, trocando os nomes:
- **Repository:** `salvar` e `listar`.
- **Controller:** `GET ""` e `POST ""`, com `prefix="/manutencoes"`.
- Também entram a linha no `entities/__init__.py` e o `include_router` no `main.py`.

**Front-end** `frontend/manutencoes.html`: copie `filiais.html` e mude estes pontos.

1. No `data()`, a lista da outra entidade:
   ```js
   manutencoes: [],
   veiculos: [],
   ```
2. No `carregar()`, busque as duas listas juntas:
   ```js
   [this.manutencoes, this.veiculos] = await Promise.all([
     api.get('/manutencoes'),
     api.get('/veiculos'),
   ]);
   ```
3. Em `methods`, uma função para mostrar a placa no lugar do id:
   ```js
   placaVeiculo(id) {
     const veiculo = this.veiculos.find((v) => v.id === id);
     return veiculo ? veiculo.placa : `#${id}`;
   },
   ```
4. Na tabela:
   ```html
   <td class="text-nowrap">{{ placaVeiculo(manutencao.veiculoId) }}</td>
   ```
5. No formulário, o select:
   ```html
   <select id="veiculo" class="form-select" v-model="form.veiculoId" required>
     <option value="" disabled>Selecione um veículo</option>
     <option v-for="veiculo in veiculos" :key="veiculo.id" :value="veiculo.id">
       {{ veiculo.descricao }} - {{ veiculo.placa }}
     </option>
   </select>
   ```
6. No `novo()`, comece com `veiculoId: ''`, para o select mostrar "Selecione". No `salvar()`, envie:
   ```js
   await api.post('/manutencoes', { veiculoId: this.form.veiculoId, descricao: this.form.descricao });
   ```

**Atenção ao excluir:** se a regra for "não excluir veículo com manutenção", faça como a R09. Em `veiculo_service.py`, `excluir`, siga o `locacao_repository.existe_por_veiculo`.

### 3.9 Regra de negócio nova

As regras ficam **sempre no service**. Basta lançar uma exceção com a mensagem: o front mostra a mensagem no alerta vermelho sozinho, sem mexer em nada no HTML.

| Exceção (`app/exceptions.py`) | Status | Quando usar                          |
|-------------------------------|--------|--------------------------------------|
| `NegocioException("...")`     | 400    | regra violada (genérico)             |
| `AcessoNegadoException("...")`| 403    | o usuário não pode fazer isso        |
| `NaoEncontradoException("...")`| 404   | não existe                           |
| `ConflitoException("...")`    | 409    | duplicado, ou estado não permite     |

Exemplo: "não pode haver duas filiais com o mesmo nome".

1. Em `filial_repository.py`, crie uma consulta, como a `existe_por_placa`:
   ```python
   def existe_por_nome(self, nome: str) -> bool:
       return self.db.scalar(select(Filial.id).where(Filial.nome == nome)) is not None
   ```
2. Em `filial_service.py`, no início do `cadastrar` (importe `ConflitoException` de `app.exceptions`):
   ```python
   if self.repository.existe_por_nome(dto.nome):
       raise ConflitoException("Já existe uma filial com este nome")
   ```
3. Teste:
   ```python
   def test_nome_unico(client, funcionario):
       client.post("/filiais", json=corpo_filial(), headers=funcionario.headers)
       r = client.post("/filiais", json=corpo_filial(), headers=funcionario.headers)
       assert r.status_code == 409
       assert r.json() == {"detail": "Já existe uma filial com este nome"}
   ```

Se a regra depender de quem está logado, o controller passa `usuario.id` / `usuario.perfil` ao service ([3.10](#310-mudar-quem-pode-acessar)).

### 3.10 Mudar quem pode acessar

São três lugares, que devem combinar:

1. **API**, no controller, no `dependencies=[...]` da rota:

   | Quem acessa       | Use                                                    |
   |-------------------|--------------------------------------------------------|
   | só FUNCIONARIO    | `Depends(exigir_perfil(Perfil.FUNCIONARIO))`           |
   | só CLIENTE        | `Depends(exigir_perfil(Perfil.CLIENTE))`               |
   | qualquer logado   | `Depends(usuario_logado)`                              |
   | público           | tire o `dependencies=[...]`                            |

   Se o service precisar saber **quem** está logado, receba o usuário como parâmetro (como em `locacao_controller.py`):
   ```python
   from app.security.dependencias import UsuarioLogado, exigir_perfil, usuario_logado

   @router.get("/minhas")
   def listar_minhas(usuario: UsuarioLogado = Depends(usuario_logado), db: Session = Depends(get_db)):
       return AlgumService(db).listar_minhas(usuario.id, usuario.perfil)
   ```
2. **Tela:** `perfis: ['CLIENTE', 'FUNCIONARIO']` no `criarApp` da página. Sem `perfis`, a tela é pública.
3. **Menu:** o `perfis` do item em `menu.html`.

**Testes que vão falhar:**
- **Mudou uma permissão da Parte I:** atualize a linha do endpoint em `backend/tests/test_permissoes.py` (lista `ENDPOINTS`).
- **Mudou a tela:** atualize `PERFIS` em `frontend/tests/frontend.test.js`.

---

## 4. Depois de cada mudança

1. **Back-end:** com `--reload`, ele reinicia sozinho ao salvar um `.py`. Se você **alterou** uma entity, apague `backend/ocar.db` e reinicie.
2. **Navegador:** F5. O `servidor.py` desliga o cache.
3. **Testes:**
   ```bash
   cd backend && .venv/bin/pytest                    # back-end
   node --test frontend/tests/frontend.test.js       # front-end (na raiz do projeto)
   ```
   O teste do front também compila o HTML e o `<script>` de cada página. Erros de digitação aparecem com o arquivo e a linha, sem precisar abrir o navegador.
4. **Falhas esperadas:** quando o professor muda o enunciado, a falha mostra o teste a atualizar.

   | Mudança                                    | Teste que falha                                  | O que fazer                                  |
   |--------------------------------------------|--------------------------------------------------|----------------------------------------------|
   | Campo novo/alterado em Usuario/Veiculo/Locacao | `test_modelo.py` (listas de campos)          | incluir o campo nas listas                   |
   | Campo novo **obrigatório** num POST da Parte I | vários + `test_insomnia.py`                  | incluir em `tests/dados.py`; o do Insomnia continua falhando (a coleção não manda o campo) |
   | Item novo no menu                          | `menu: cada perfil vê...` (front)                | incluir o título na lista do perfil          |
   | Permissão diferente                        | `test_permissoes.py` / `PERFIS` (front)          | atualizar a linha                            |
   | Mensagem de erro diferente                 | o teste da regra                                 | atualizar o texto esperado                   |

   Uma falha **em parte que você não mexeu** quer dizer que algo quebrou sem querer.

---

## 5. Quando algo dá errado

Primeiro passo, sempre: **F12 → Console** no navegador e o **terminal do uvicorn**.

| Sintoma                                                  | Causa provável                                                 | Correção                                                      |
|----------------------------------------------------------|----------------------------------------------------------------|---------------------------------------------------------------|
| Tela em branco, ou aparecendo `{{ ... }}`                | erro de sintaxe no `<script>` (vírgula, chave, parêntese) ou no template | o Console mostra a linha; o teste do front também (`veiculos.html:97 -> Unexpected identifier`) |
| Teste do front: `Unnecessary value binding used alongside v-model` | o input tem `:value` e `v-model` juntos                 | apague o `:value`; o `v-model` já preenche o campo            |
| Teste do front: `Element is missing end tag`             | faltou fechar uma tag (`</div>`, `</table>`...)                | confira os pares de abertura/fechamento perto do trecho alterado |
| Coluna ou campo sempre vazio                             | nome diferente entre HTML, `data()` e DTO (`form.Cor` × `cor`) | Console: aviso `Property "x" was accessed during render but is not defined` |
| Alerta `campo: Field required`                           | o `api.post` não envia o campo, ou com outro nome              | compare o `corpo` do `salvar()` com o RequestDTO              |
| Alerta `Not Found` numa rota nova                        | faltou `app.include_router(...)` no `main.py`, ou URL ≠ `prefix` | `main.py` e o controller                                      |
| Alerta `Method Not Allowed`                              | método diferente (front `api.patch`, controller `@router.put`) | use o mesmo nos dois                                          |
| `id: Input should be a valid integer` em `/x/existe`     | rota fixa declarada depois de `/{id}`                          | mova a rota fixa para cima no controller                      |
| Terminal: `no such column` / `no such table`             | entity alterada e banco antigo, ou faltou importar em `entities/__init__.py` | apague `backend/ocar.db` e reinicie / adicione o import |
| Alerta `Não foi possível conectar ao servidor...`        | back-end parado ou com erro ao subir                           | veja o terminal do uvicorn                                    |
| Volta sozinho para o login                               | token expirou, ou o banco foi apagado (usuário não existe mais)| cadastre e entre de novo                                      |
| Tela nova volta para o menu                              | o perfil não está no `perfis` da página                        | `criarApp({ perfis: [...] })`                                 |
| Card não aparece no menu                                 | o perfil não está no `perfis` do item                          | `menu.html`                                                   |
| `test_camadas.py` falha                                  | controller importou entity/repository, ou service importou `fastapi` | siga as camadas: controller → service → repository     |
