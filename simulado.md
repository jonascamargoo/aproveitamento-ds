# Simulado da Parte II (2 horas)

Uma prova de 2 horas com 5 questões no estilo do que o professor pode pedir. Os tipos de alteração estão misturados e o front-end tem mais peso: todas as questões mexem na tela, e três também passam pelo back-end. Cada questão traz o pedido, como conferir o resultado, uma dica e o gabarito.

| #  | Pedido                                        | O que treina                    | Front | Back | Tempo-alvo |
|----|-----------------------------------------------|---------------------------------|:-----:|:----:|------------|
| 1  | Disponibilidade colorida na lista de veículos | classe condicional no HTML      | ✔     |      | 10 min     |
| 2  | Filtro por situação em Gerenciar Locações     | `computed` e `<select>`         | ✔     |      | 20 min     |
| 3  | Veículo locado não pode ser alterado          | regra de negócio + botão        | ✔     | ✔    | 20 min     |
| 4  | Valor da diária no veículo                    | campo novo nas duas pontas      | ✔     | ✔    | 40 min     |
| 5  | Tela "Veículos Disponíveis" para o cliente    | tela nova + endpoint novo       | ✔     | ✔    | 35 min     |

O tempo-alvo é uma estimativa, fazendo à mão com o [`guia-alteracoes.md`](guia-alteracoes.md) aberto. O total dá umas 2h, então terminar dentro do tempo é um ótimo sinal.

Depois da prova há um **treino extra**, fora das 2h, com mais 5 pedidos: saudação no menu, confirmar senha, uma locação por cliente, cancelar locação e entidade nova.

Os gabaritos foram testados em 18/10/2026 numa cópia do projeto, de três formas: testes do back-end, testes do front-end e uso das telas no navegador. Foram testadas a prova sozinha e a prova junto com o treino extra.

## Como fazer

1. **Faça numa cópia** para não mexer no projeto de verdade. Na pasta que contém o projeto:
   ```bash
   cp -R aproveitamento-ds simulado-ocar
   cd simulado-ocar
   ```
   - A cópia usa o mesmo ambiente do back-end, então os comandos são os de sempre.
   - Não rode o projeto original ao mesmo tempo, porque os dois usam as portas 8080 e 5500.
   - No fim, apague a pasta `simulado-ocar`.
2. **Ligue um cronômetro de 2h para a prova inteira** e anote a hora em que terminou cada questão.
3. **Tente antes de abrir a dica ou o gabarito.** Consultar o `guia-alteracoes.md` vale, porque na prova você também vai usá-lo.
4. **Depois de cada questão, rode os testes:**
   ```bash
   cd backend && .venv/bin/pytest && cd ..          # back-end
   node --test frontend/tests/frontend.test.js      # front-end
   ```
   Às vezes um teste antigo vai falhar de propósito, porque o pedido mudou uma regra da Parte I. Ajustar esses testes faz parte do treino, e o gabarito diz quais são.
5. **Se travar,** veja a seção 5 do guia, "Quando algo dá errado". Ela tem os erros mais comuns.

## Estratégia para as 2 horas

- **Leia todas as questões antes de começar.** Leva 2 minutos e evita surpresas.
- **Faça na ordem.** As primeiras são rápidas e garantem pontos cedo.
- **Travou mais de 10 minutos?** Pule para a próxima e volte depois.
- **Confira cada questão assim que terminar,** na tela (F5) e com os testes. Um erro achado na hora é fácil de corrigir; vários juntos no fim, não.
- **Nos últimos 10 minutos, não comece nada grande.** Confira se o back-end sobe e se as telas abrem. Se uma alteração quebrou uma tela e não dá tempo de consertar, desfaça a alteração (Ctrl+Z no arquivo) para entregar o projeto funcionando.
---

## Questão 1. Disponibilidade colorida na lista de veículos

> **Pedido:** "Na lista de veículos, a coluna Disponível deve aparecer como um selo: verde para *Sim* e vermelho para *Não*."

**Como conferir:** cadastre dois veículos e crie uma locação com um deles. O veículo locado aparece com o selo vermelho.

<details>
<summary>Dica</summary>

Só muda o `frontend/veiculos.html`. A tela Gerenciar Locações já faz isso com a situação: procure por `badge` em `gerenciarlocacoes.html`.
</details>

<details>
<summary>Gabarito</summary>

`frontend/veiculos.html`, troque a linha `<td>{{ fmt.simNao(veiculo.disponivel) }}</td>` por:

```html
<td>
  <span class="badge" :class="veiculo.disponivel ? 'text-bg-success' : 'text-bg-danger'">
    {{ fmt.simNao(veiculo.disponivel) }}
  </span>
</td>
```

O `:class` com `? :` funciona como o `x if condicao else y` do Python.
</details>

---

## Questão 2. Filtro por situação em Gerenciar Locações

> **Pedido:** "Em Gerenciar Locações, coloque um seletor para filtrar a lista: *Todas*, *Em andamento* ou *Finalizadas*."

**Como conferir:** crie duas locações e finalize uma. Cada opção do seletor mostra só as locações daquela situação.

<details>
<summary>Dica</summary>

Só muda o `frontend/gerenciarlocacoes.html`. É a mesma ideia da busca da seção 3.5 do guia: uma variável no `data()`, um `computed` que filtra a lista e o `v-for` usando o `computed`.
</details>

<details>
<summary>Gabarito</summary>

`frontend/gerenciarlocacoes.html`:

1. No `data()`, depois de `form: {},`:
   ```js
   filtroSituacao: '', // '' = todas
   ```
2. No `computed`, antes do `opcoesVeiculo()`:
   ```js
   locacoesFiltradas() {
     if (!this.filtroSituacao) return this.locacoes;
     return this.locacoes.filter((l) => l.situacao === this.filtroSituacao);
   },
   ```
3. Logo depois de `<div v-if="modo === 'lista'" class="table-responsive">`:
   ```html
   <select class="form-select mb-3" style="max-width: 250px" v-model="filtroSituacao">
     <option value="">Todas as situações</option>
     <option value="EM_ANDAMENTO">Em andamento</option>
     <option value="FINALIZADA">Finalizadas</option>
   </select>
   ```
4. Troque `locacoes` por `locacoesFiltradas` em dois lugares:
   - `v-for="locacao in locacoesFiltradas"`
   - `v-if="locacoesFiltradas.length === 0"`

Opcional: troque o texto "Nenhuma locação cadastrada." por "Nenhuma locação encontrada.", que faz mais sentido com o filtro.
</details>

---

## Questão 3. Veículo locado não pode ser alterado

> **Pedido:** "Não deve ser possível alterar um veículo que está em locação. A API responde **409** com a mensagem *Veículo em locação não pode ser alterado*, e na tela o botão Editar fica desabilitado para esse veículo."

**Como conferir:** loque um veículo. Na lista de veículos, o botão Editar dele fica cinza. Pelo Swagger, o `PATCH /veiculos/{id}` desse veículo responde 409.

<details>
<summary>Dica</summary>

- **Back-end:** a regra fica no método `alterar_descricao` de `backend/app/services/veiculo_service.py`. Um veículo em locação é um veículo com `disponivel` falso.
- **Front-end:** no botão Editar de `veiculos.html`, o `:disabled` recebe uma expressão, como no input da placa.
- **Teste que vai falhar:** um teste antigo diz o contrário da regra nova.
</details>

<details>
<summary>Gabarito</summary>

`backend/app/services/veiculo_service.py`, no `alterar_descricao`, logo depois de `veiculo = self._buscar_entidade(id)`:

```python
# Nova regra: veículo em locação (indisponível) não pode ser alterado
if not veiculo.disponivel:
    raise ConflitoException("Veículo em locação não pode ser alterado")
```

`frontend/veiculos.html`, no botão Editar, acrescente o `:disabled`:

```html
<button class="btn btn-sm btn-outline-primary me-1" @click="editar(veiculo)" title="Editar"
        :disabled="!veiculo.disponivel">
```

**Testes**, em `backend/tests/test_locacoes.py`: o `test_alterar_descricao_de_veiculo_locado_nao_muda_disponibilidade` fazia exatamente o que agora é proibido. Troque o teste inteiro por:

```python
def test_veiculo_em_locacao_nao_pode_ser_alterado(client, api, cliente, funcionario, veiculo):
    api.locacao(funcionario.headers, veiculo["id"], cliente.id)
    r = client.patch(f"/veiculos/{veiculo['id']}", json={"descricao": "Nova"}, headers=funcionario.headers)
    assert r.status_code == 409
    assert r.json() == {"detail": "Veículo em locação não pode ser alterado"}
```
</details>

---

## Questão 4. Valor da diária no veículo

> **Pedido:** "Todo veículo passa a ter o valor da diária, obrigatório e maior que zero. Ele é informado no cadastro, não muda na edição e aparece na lista formatado em reais (*R$ 150,00*)."

**Como conferir:**
- Apague o `backend/ocar.db` e reinicie o back-end.
- Cadastre um veículo com diária `75.5`: a lista mostra *R$ 75,50*.
- Na edição, o campo aparece desabilitado.

<details>
<summary>Dica</summary>

- **Receita:** é a 3.3 do guia (campo `cor`), com um campo decimal.
- **Tipos:** a tabela da 3.4 tem o `Mapped[float]`, o `Field(gt=0)` e o input numérico.
- **Formatação:** a 3.6 tem o formatador `moeda`.
- **Testes:** o guia diz quais falham com um campo novo obrigatório.
</details>

<details>
<summary>Gabarito</summary>

O campo se chama `diaria` em todos os lugares: entity, DTO, HTML e JSON. O `model_validate` do service copia os atributos da entity para o DTO **pelo nome**, então os nomes precisam ser iguais. Se o professor exigir `valorDiaria` no JSON, use `valorDiaria` também na entity.

**Back-end:**

1. `backend/app/entities/veiculo.py`, no fim da classe:
   ```python
   diaria: Mapped[float]
   ```
2. `backend/app/dtos/veiculo_dto.py`:
   - no `VeiculoRequestDTO`:
     ```python
     diaria: float = Field(gt=0)
     ```
   - no `VeiculoResponseDTO`:
     ```python
     diaria: float
     ```
3. `backend/app/services/veiculo_service.py`, no `cadastrar`:
   ```python
   veiculo = Veiculo(placa=dto.placa, descricao=dto.descricao, disponivel=True, diaria=dto.diaria)
   ```
4. Apague o `backend/ocar.db`. A tabela mudou e precisa ser recriada.

**Front-end:**

1. `frontend/js/app.js`, no objeto `fmt`:
   ```js
   moeda: (valor) => Number(valor).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }),
   ```
2. `frontend/veiculos.html`, em 5 lugares:
   - **Cabeçalho da tabela,** depois de `<th>Placa</th>`:
     ```html
     <th>Diária</th>
     ```
   - **Linha da tabela,** depois do `<td>` da placa:
     ```html
     <td class="text-nowrap">{{ fmt.moeda(veiculo.diaria) }}</td>
     ```
   - **Linha "Nenhum veículo cadastrado":** `colspan="4"` passa a ser `colspan="5"`.
   - **Formulário,** um bloco novo depois do bloco da placa:
     ```html
     <div class="col-12 col-md-6">
       <label class="form-label" for="diaria">Valor da diária (R$)</label>
       <input id="diaria" type="number" step="0.01" min="0.01" class="form-control"
              v-model.number="form.diaria" :disabled="!!form.id" required>
     </div>
     ```
   - **`novo()` e `salvar()`:**
     ```js
     this.form = { id: null, descricao: '', placa: '', disponivel: true, diaria: '' };
     ```
     ```js
     await api.post('/veiculos', { placa: this.form.placa, descricao: this.form.descricao, diaria: this.form.diaria });
     ```

**Testes:**

1. `backend/tests/dados.py`, para que todos os testes passem a enviar o campo:
   ```python
   return {"placa": "ABC1D23", "descricao": "Toyota Corolla", "diaria": 150.0, **campos}
   ```
2. `backend/tests/test_modelo.py`, acrescente `"diaria"` em três listas:
   ```python
   (Veiculo, {"id", "placa", "descricao", "disponivel", "diaria"}),
   ```
   ```python
   (VeiculoRequestDTO, ["placa", "descricao", "diaria"]),
   (VeiculoResponseDTO, ["id", "placa", "descricao", "disponivel", "diaria"]),
   ```
3. Opcional: um teste do campo, no fim de `backend/tests/test_veiculos.py`:
   ```python
   def test_diaria(client, funcionario):
       r = client.post("/veiculos", json=corpo_veiculo(diaria=99.9), headers=funcionario.headers)
       assert r.status_code == 201
       assert r.json()["diaria"] == 99.9
       r = client.post("/veiculos", json=corpo_veiculo(placa="XYZ9A99", diaria=0), headers=funcionario.headers)
       assert r.status_code == 422
   ```

Antes do passo 1, quase todos os testes falham. É esperado, porque os corpos dos testes ainda não mandam a diária. Depois dos passos 1 e 2, só o `test_insomnia.py` falha, também esperado: a coleção da Parte I não manda a diária.
</details>

---

## Questão 5. Tela "Veículos Disponíveis" para o cliente

> **Pedido:** "O cliente deve ter, no menu, a tela *Veículos Disponíveis*, com a descrição e a placa dos veículos que podem ser alugados. Crie o endpoint `GET /veiculos/disponiveis`, liberado para qualquer usuário logado."

**Como conferir:** logue como cliente. O card novo aparece no menu, e a tela lista só os veículos disponíveis. Um veículo locado some da lista e volta quando a locação é finalizada.

<details>
<summary>Dica</summary>

- **Back-end:** endpoint novo, passando por controller, service e repository. O `listar` de veículos é o modelo.
- **Cuidado com a ordem das rotas** no controller: `/disponiveis` precisa vir **antes** de `/{id}`, igual ao `/existe`. Se ficar depois, a resposta é *id: Input should be a valid integer*.
- **Front-end:** a tela mais parecida é a `minhaslocacoes.html`, só leitura e do cliente. Copie e simplifique.
- **Testes que vão falhar:** os do front.
</details>

<details>
<summary>Gabarito</summary>

**Back-end:**

1. `backend/app/repositories/veiculo_repository.py`:
   ```python
   def listar_disponiveis(self) -> list[Veiculo]:
       return list(self.db.scalars(select(Veiculo).where(Veiculo.disponivel).order_by(Veiculo.id)))
   ```
2. `backend/app/services/veiculo_service.py`:
   ```python
   def listar_disponiveis(self) -> list[VeiculoResponseDTO]:
       return [VeiculoResponseDTO.model_validate(v) for v in self.repository.listar_disponiveis()]
   ```
3. `backend/app/controllers/veiculo_controller.py`, **antes** do `@router.get("/{id}", ...)`:
   ```python
   # Também antes de /{id}
   @router.get("/disponiveis", dependencies=[Depends(usuario_logado)])
   def listar_disponiveis(db: Session = Depends(get_db)) -> list[VeiculoResponseDTO]:
       return VeiculoService(db).listar_disponiveis()
   ```

**Front-end:**

1. `frontend/menu.html`, uma linha na lista `itens`:
   ```js
   { titulo: 'Veículos Disponíveis', icone: 'bi-car-front', url: 'veiculosdisponiveis.html', perfis: ['CLIENTE'] },
   ```
2. `frontend/veiculosdisponiveis.html`, um arquivo novo:

   <details>
   <summary>Arquivo completo</summary>

   ```html
   <!DOCTYPE html>
   <html lang="pt-BR">
   <head>
     <meta charset="UTF-8">
     <meta name="viewport" content="width=device-width, initial-scale=1">
     <title>OCar - Veículos Disponíveis</title>
     <link rel="stylesheet" href="vendor/bootstrap/bootstrap.min.css">
     <link rel="stylesheet" href="vendor/bootstrap-icons/bootstrap-icons.min.css">
     <link rel="stylesheet" href="css/style.css">
   </head>
   <body class="bg-light">
   <div id="app" v-cloak class="d-flex flex-column min-vh-100">
     <app-header></app-header>

     <main class="container py-4 flex-grow-1">
       <h1 class="h4 mb-3">Veículos Disponíveis</h1>

       <div v-if="erro" class="alert alert-danger">{{ erro }}</div>

       <div class="table-responsive">
         <table class="table table-striped bg-white border">
           <thead class="table-light">
             <tr>
               <th>Descrição</th>
               <th>Placa</th>
             </tr>
           </thead>
           <tbody>
             <tr v-for="veiculo in veiculos" :key="veiculo.id">
               <td>{{ veiculo.descricao }}</td>
               <td class="text-nowrap">{{ veiculo.placa }}</td>
             </tr>
             <tr v-if="veiculos.length === 0">
               <td colspan="2" class="text-center text-secondary">Nenhum veículo disponível no momento.</td>
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
       perfis: ['CLIENTE'],
       data() {
         return {
           veiculos: [],
           erro: '',
         };
       },
       async mounted() {
         try {
           this.veiculos = await api.get('/veiculos/disponiveis');
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

**Testes:**

1. `frontend/tests/frontend.test.js`:
   - em `PERFIS`:
     ```js
     'veiculosdisponiveis.html': ["'CLIENTE'"],
     ```
   - no teste "menu: cada perfil vê...", na lista do cliente:
     ```js
     assert.deepEqual(para('CLIENTE'), ['Meus Dados', 'Minhas Locações', 'Veículos Disponíveis']);
     ```
2. Teste do endpoint, no fim de `backend/tests/test_veiculos.py`:
   ```python
   def test_listar_disponiveis(client, api, cliente, funcionario):
       alugado = api.veiculo(funcionario.headers)
       livre = api.veiculo(funcionario.headers, placa="XYZ9A99")
       api.locacao(funcionario.headers, alugado["id"], cliente.id)

       r = client.get("/veiculos/disponiveis", headers=cliente.headers)
       assert r.status_code == 200
       assert [v["id"] for v in r.json()] == [livre["id"]]
       assert client.get("/veiculos/disponiveis").status_code == 401
   ```
</details>

---

# Treino extra (fora das 2 horas)

Mais 5 pedidos para treinar depois da prova ou em outro dia, numa cópia nova. Cada um funciona sozinho.
---

## Extra A. Saudação no menu

> **Pedido:** "No menu, mostre uma saudação com o login de quem está logado, por exemplo: *Olá, maria!*"

**Como conferir:** logue como cliente e depois como funcionário. A saudação aparece acima dos cards, com o login certo.

<details>
<summary>Dica</summary>

Só muda o `frontend/menu.html`. O rodapé já mostra o login: veja como o `AppFooter`, em `frontend/js/app.js`, faz isso.
</details>

<details>
<summary>Gabarito</summary>

`frontend/menu.html`, logo depois de `<main class="container py-5 flex-grow-1">`:

```html
<h1 class="h4 text-center mb-4">Olá, {{ usuarioLogado.login }}!</h1>
```

O `usuarioLogado` existe em todas as telas protegidas. Ele é criado no `criarApp`, em `app.js`, com o `id`, o `login` e o `perfil` lidos do token.
</details>

---

## Extra B. Confirmar senha no cadastro de usuário

> **Pedido:** "Na tela de registro de usuários, inclua o campo *Confirmar senha*. Se as senhas forem diferentes, mostre *As senhas não conferem.* e não cadastre."

**Como conferir:**
- Senhas diferentes: aparece o alerta vermelho e o usuário não é criado.
- Senhas iguais: o cadastro funciona e você vai para a tela de login.

<details>
<summary>Dica</summary>

Só muda o `frontend/usuario.html`, em três lugares: o input, o `data()` e o método `cadastrar()`. A tela `meusdados.html` já faz essa conferência na troca de senha, então copie de lá.
</details>

<details>
<summary>Gabarito</summary>

`frontend/usuario.html`:

1. Depois do bloco da senha (o `<div class="col-12 col-md-4">` que tem `id="senha"`):
   ```html
   <div class="col-12 col-md-4">
     <label class="form-label" for="confirmacao">Confirmar senha</label>
     <input id="confirmacao" type="password" class="form-control" v-model="confirmacao" required>
   </div>
   ```
2. No `data()`, depois de `loginEmUso: false,`:
   ```js
   confirmacao: '',
   ```
3. No `cadastrar()`, logo depois de `this.erro = '';`:
   ```js
   if (this.usuario.senha !== this.confirmacao) {
     this.erro = 'As senhas não conferem.';
     return;
   }
   ```

A `confirmacao` fica fora do objeto `usuario` de propósito, para não ser enviada à API no `api.post('/usuarios', this.usuario)`.
</details>

---

## Extra C. Cliente com uma locação em andamento por vez

> **Pedido:** "Um cliente não pode ter mais de uma locação em andamento. Nesse caso, a API responde **409** com a mensagem *Cliente já possui uma locação em andamento*."

**Como conferir:**
- Crie uma locação para a maria e tente criar outra com outro veículo: aparece o alerta vermelho com a mensagem.
- Finalize a primeira e tente de novo: agora funciona.

<details>
<summary>Dica</summary>

- **Onde fica a regra:** no método `criar` de `backend/app/services/locacao_service.py` (seção 3.9 do guia).
- **O que você já tem:** o `LocacaoRepository` tem o método `listar_por_cliente`.
- **Erro comum:** o service **não tem** `self.db`; use os repositories que ele já tem.
- **Teste que vai falhar:** um teste antigo cria duas locações em andamento para a mesma cliente.
</details>

<details>
<summary>Gabarito</summary>

`backend/app/services/locacao_service.py`, no `criar`, logo depois do `raise NegocioException("O usuário informado não possui perfil CLIENTE")`:

```python
# Nova regra: o cliente só pode ter uma locação em andamento
locacoes_do_cliente = self.repository.listar_por_cliente(cliente.id)
if any(l.situacao == Situacao.EM_ANDAMENTO for l in locacoes_do_cliente):
    raise ConflitoException("Cliente já possui uma locação em andamento")
```

O front não muda: o alerta vermelho já mostra qualquer mensagem de erro da API.

**Testes**, em `backend/tests/test_locacoes.py`:

1. Vai falhar o `test_r07_cada_um_lista_so_as_suas`, porque a maria recebia duas locações em andamento. Finalize a primeira antes de criar a segunda:
   ```python
   l1 = api.locacao(funcionario.headers, v1["id"], maria.id)
   client.patch(f"/locacoes/{l1['id']}/finalizar", headers=funcionario.headers)  # nova regra: uma em andamento por cliente
   l2 = api.locacao(pedro.headers, v2["id"], maria.id)
   ```
2. Teste da regra nova, no fim do arquivo:
   ```python
   def test_cliente_so_pode_ter_uma_locacao_em_andamento(client, api, cliente, funcionario, veiculo):
       primeira = api.locacao(funcionario.headers, veiculo["id"], cliente.id)
       outro_veiculo = api.veiculo(funcionario.headers, placa="XYZ9A99")

       r = client.post("/locacoes", json=corpo_locacao(outro_veiculo["id"], cliente.id), headers=funcionario.headers)
       assert r.status_code == 409
       assert r.json() == {"detail": "Cliente já possui uma locação em andamento"}

       # depois de finalizar a primeira, pode alugar de novo
       client.patch(f"/locacoes/{primeira['id']}/finalizar", headers=funcionario.headers)
       api.locacao(funcionario.headers, outro_veiculo["id"], cliente.id)
   ```
</details>

---

## Extra D. Cancelar locação

> **Pedido:** "O funcionário responsável pode cancelar uma locação em andamento.
> - A situação passa a ser *Cancelada* e o veículo volta a ficar disponível.
> - O endpoint é `PATCH /locacoes/{id}/cancelar`.
> - Na tela Gerenciar, aparece o botão *Cancelar locação* ao lado de *Finalizar*."

**Como conferir:**
- Crie uma locação, abra "Gerenciar" e clique em "Cancelar locação". A lista mostra *Cancelada* e o veículo volta a aparecer como disponível.
- Cancelar de novo, pelo Swagger, responde 409.

<details>
<summary>Dica</summary>

É uma cópia do "finalizar", que já existe em todas as camadas: enum, service, controller, `fmt.situacao` e a tela. Procure por `finalizar` e `FINALIZADA` no projeto e repita o caminho com "cancelar". Não precisa apagar o `ocar.db`, porque a coluna da situação já é texto.
</details>

<details>
<summary>Gabarito</summary>

**Back-end:**

1. `backend/app/entities/enums.py`, no `Situacao`:
   ```python
   CANCELADA = "CANCELADA"
   ```
2. `backend/app/services/locacao_service.py`, um método novo antes do `_buscar_entidade`:
   ```python
   def cancelar(self, id: int, funcionario_id: int) -> LocacaoResponseDTO:
       locacao = self._buscar_entidade(id)
       # Nova regra: igual ao finalizar, mas a situação vira CANCELADA
       if locacao.funcionario_id != funcionario_id:
           raise AcessoNegadoException("Apenas o funcionário responsável pode cancelar esta locação")
       if locacao.situacao != Situacao.EM_ANDAMENTO:
           raise ConflitoException("Somente locações em andamento podem ser canceladas")
       locacao.situacao = Situacao.CANCELADA
       locacao.veiculo.disponivel = True
       return self._para_dto(self.repository.salvar(locacao))
   ```
3. `backend/app/controllers/locacao_controller.py`, no fim:
   ```python
   @router.patch("/{id}/cancelar")
   def cancelar(
       id: int,
       funcionario: UsuarioLogado = Depends(exigir_perfil(Perfil.FUNCIONARIO)),
       db: Session = Depends(get_db),
   ) -> LocacaoResponseDTO:
       return LocacaoService(db).cancelar(id, funcionario.id)
   ```

**Front-end:**

1. `frontend/js/app.js`, no `fmt.situacao`:
   ```js
   situacao: (situacao) => ({ EM_ANDAMENTO: 'Em andamento', FINALIZADA: 'Finalizada', CANCELADA: 'Cancelada' })[situacao] || situacao,
   ```
2. `frontend/gerenciarlocacoes.html`. Troque o botão Finalizar e o `<span v-else></span>` logo abaixo dele por:
   ```html
   <div v-if="form.id && form.situacao === 'EM_ANDAMENTO'" class="d-flex gap-2">
     <button type="button" class="btn btn-warning" @click="finalizar">
       <i class="bi bi-flag"></i> Finalizar
     </button>
     <button type="button" class="btn btn-outline-danger" @click="cancelar">
       <i class="bi bi-x-circle"></i> Cancelar locação
     </button>
   </div>
   <span v-else></span>
   ```
   Depois, em `methods`, acrescente um método depois do `finalizar()`:
   ```js
   async cancelar() {
     if (!confirm('Cancelar esta locação?')) return;
     this.limparMensagens();
     try {
       await api.patch(`/locacoes/${this.form.id}/cancelar`);
       this.sucesso = 'Locação cancelada com sucesso.';
       this.modo = 'lista';
       await this.carregar();
     } catch (e) {
       this.erro = e.message;
     }
   },
   ```
3. **Se fez a questão 2 (filtro),** inclua a opção nele:
   ```html
   <option value="CANCELADA">Canceladas</option>
   ```
4. **Opcional: selo vermelho para Cancelada.** O `:class` atual só conhece duas cores. Em `gerenciarlocacoes.html` e `minhaslocacoes.html`, troque o `<span class="badge" ...>` por:
   ```html
   <span class="badge" :class="corDaSituacao[locacao.situacao]">
   ```
   E acrescente no `data()` das duas telas:
   ```js
   corDaSituacao: { EM_ANDAMENTO: 'text-bg-warning', FINALIZADA: 'text-bg-secondary', CANCELADA: 'text-bg-danger' },
   ```

**Testes:**

1. Vai falhar o `test_enums`, em `backend/tests/test_modelo.py`. Atualize a lista:
   ```python
   assert [s.name for s in Situacao] == ["EM_ANDAMENTO", "FINALIZADA", "CANCELADA"]
   ```
2. Testes novos, no fim de `backend/tests/test_locacoes.py`:
   ```python
   def test_cancelar(client, api, cliente, funcionario, veiculo):
       locacao = api.locacao(funcionario.headers, veiculo["id"], cliente.id)
       r = client.patch(f"/locacoes/{locacao['id']}/cancelar", headers=funcionario.headers)
       assert r.status_code == 200
       assert r.json()["situacao"] == "CANCELADA"
       assert disponivel(client, funcionario.headers, veiculo["id"]) is True

       # só locação em andamento pode ser cancelada
       r = client.patch(f"/locacoes/{locacao['id']}/cancelar", headers=funcionario.headers)
       assert r.status_code == 409
       assert r.json() == {"detail": "Somente locações em andamento podem ser canceladas"}


   def test_so_o_funcionario_responsavel_cancela(client, api, cliente, funcionario, veiculo):
       locacao = api.locacao(funcionario.headers, veiculo["id"], cliente.id)
       outro_func = api.usuario("pedro", "FUNCIONARIO")
       assert client.patch(f"/locacoes/{locacao['id']}/cancelar", headers=outro_func.headers).status_code == 403
       assert client.patch(f"/locacoes/{locacao['id']}/cancelar", headers=cliente.headers).status_code == 403
   ```
</details>

---

## Extra E. Cadastro de acessórios

> **Pedido:** "Crie o cadastro de acessórios (ex.: cadeirinha de bebê, GPS), com **nome** e **valor da diária**.
> - Só o funcionário acessa: listar, cadastrar, alterar e excluir.
> - Não pode haver dois acessórios com o mesmo nome (**409**, *Já existe um acessório com este nome*).
> - A tela fica no menu do funcionário."

**Como conferir:** logue como funcionário, abra "Acessórios" no menu, cadastre, altere e exclua um acessório. Tente cadastrar dois com o mesmo nome e confira a mensagem.

<details>
<summary>Dica</summary>

- **Receita:** é a 3.7 do guia (Filial), trocando os nomes e o campo `cidade` por `diaria`. O campo decimal é igual ao da questão 4.
- **Nome único:** é o exemplo da 3.9.
- **Arquivos novos:** 5 no back-end e 1 no front.
- **Arquivos alterados:** `entities/__init__.py`, `main.py` e `menu.html`.
- **Banco:** tabela nova é criada sozinha, então não precisa apagar o `ocar.db`.
</details>

<details>
<summary>Gabarito</summary>

**Back-end:** 5 arquivos novos.

<details>
<summary><code>backend/app/entities/acessorio.py</code></summary>

```python
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Acessorio(Base):
    __tablename__ = "acessorio"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), unique=True)
    diaria: Mapped[float]
```
</details>

<details>
<summary><code>backend/app/dtos/acessorio_dto.py</code></summary>

```python
from pydantic import BaseModel, ConfigDict, Field

from app.dtos.campos import TextoObrigatorio


class AcessorioRequestDTO(BaseModel):
    nome: TextoObrigatorio = Field(max_length=100)
    diaria: float = Field(gt=0)


class AcessorioResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    diaria: float
```
</details>

<details>
<summary><code>backend/app/repositories/acessorio_repository.py</code></summary>

```python
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.entities.acessorio import Acessorio


class AcessorioRepository:
    def __init__(self, db: Session):
        self.db = db

    def salvar(self, acessorio: Acessorio) -> Acessorio:
        self.db.add(acessorio)
        self.db.commit()
        self.db.refresh(acessorio)
        return acessorio

    def excluir(self, acessorio: Acessorio) -> None:
        self.db.delete(acessorio)
        self.db.commit()

    def buscar_por_id(self, id: int) -> Acessorio | None:
        return self.db.get(Acessorio, id)

    def listar(self) -> list[Acessorio]:
        return list(self.db.scalars(select(Acessorio).order_by(Acessorio.id)))

    def existe_por_nome(self, nome: str) -> bool:
        return self.db.scalar(select(Acessorio.id).where(Acessorio.nome == nome)) is not None
```
</details>

<details>
<summary><code>backend/app/services/acessorio_service.py</code></summary>

```python
from sqlalchemy.orm import Session

from app.dtos.acessorio_dto import AcessorioRequestDTO, AcessorioResponseDTO
from app.entities.acessorio import Acessorio
from app.exceptions import ConflitoException, NaoEncontradoException
from app.repositories.acessorio_repository import AcessorioRepository


class AcessorioService:
    def __init__(self, db: Session):
        self.repository = AcessorioRepository(db)

    def listar(self) -> list[AcessorioResponseDTO]:
        return [AcessorioResponseDTO.model_validate(a) for a in self.repository.listar()]

    def buscar(self, id: int) -> AcessorioResponseDTO:
        return AcessorioResponseDTO.model_validate(self._buscar_entidade(id))

    def cadastrar(self, dto: AcessorioRequestDTO) -> AcessorioResponseDTO:
        if self.repository.existe_por_nome(dto.nome):
            raise ConflitoException("Já existe um acessório com este nome")
        acessorio = Acessorio(nome=dto.nome, diaria=dto.diaria)
        return AcessorioResponseDTO.model_validate(self.repository.salvar(acessorio))

    def alterar(self, id: int, dto: AcessorioRequestDTO) -> AcessorioResponseDTO:
        acessorio = self._buscar_entidade(id)
        if dto.nome != acessorio.nome and self.repository.existe_por_nome(dto.nome):
            raise ConflitoException("Já existe um acessório com este nome")
        acessorio.nome = dto.nome
        acessorio.diaria = dto.diaria
        return AcessorioResponseDTO.model_validate(self.repository.salvar(acessorio))

    def excluir(self, id: int) -> None:
        self.repository.excluir(self._buscar_entidade(id))

    def _buscar_entidade(self, id: int) -> Acessorio:
        acessorio = self.repository.buscar_por_id(id)
        if acessorio is None:
            raise NaoEncontradoException("Acessório não encontrado")
        return acessorio
```

No `alterar`, o `dto.nome != acessorio.nome` deixa salvar o acessório mantendo o próprio nome.
</details>

<details>
<summary><code>backend/app/controllers/acessorio_controller.py</code></summary>

```python
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dtos.acessorio_dto import AcessorioRequestDTO, AcessorioResponseDTO
from app.entities.enums import Perfil
from app.security.dependencias import exigir_perfil
from app.services.acessorio_service import AcessorioService

router = APIRouter(prefix="/acessorios", tags=["Acessórios"])


@router.get("", dependencies=[Depends(exigir_perfil(Perfil.FUNCIONARIO))])
def listar(db: Session = Depends(get_db)) -> list[AcessorioResponseDTO]:
    return AcessorioService(db).listar()


@router.get("/{id}", dependencies=[Depends(exigir_perfil(Perfil.FUNCIONARIO))])
def buscar(id: int, db: Session = Depends(get_db)) -> AcessorioResponseDTO:
    return AcessorioService(db).buscar(id)


@router.post("", status_code=status.HTTP_201_CREATED, dependencies=[Depends(exigir_perfil(Perfil.FUNCIONARIO))])
def cadastrar(dto: AcessorioRequestDTO, db: Session = Depends(get_db)) -> AcessorioResponseDTO:
    return AcessorioService(db).cadastrar(dto)


@router.patch("/{id}", dependencies=[Depends(exigir_perfil(Perfil.FUNCIONARIO))])
def alterar(id: int, dto: AcessorioRequestDTO, db: Session = Depends(get_db)) -> AcessorioResponseDTO:
    return AcessorioService(db).alterar(id, dto)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(exigir_perfil(Perfil.FUNCIONARIO))])
def excluir(id: int, db: Session = Depends(get_db)) -> None:
    AcessorioService(db).excluir(id)
```
</details>

E 2 arquivos alterados:

- `backend/app/entities/__init__.py`, no fim:
  ```python
  from app.entities.acessorio import Acessorio
  ```
- `backend/app/main.py`, no import dos controllers e nos `include_router`:
  ```python
  from app.controllers import acessorio_controller, autenticacao_controller, locacao_controller, usuario_controller, veiculo_controller
  ```
  ```python
  app.include_router(acessorio_controller.router)
  ```

**Front-end:**

1. `frontend/menu.html`, uma linha na lista `itens`:
   ```js
   { titulo: 'Acessórios', icone: 'bi-bag-plus', url: 'acessorios.html', perfis: ['FUNCIONARIO'] },
   ```
2. `frontend/acessorios.html`, um arquivo novo. Copie o `filiais.html` da receita 3.7 do guia e faça estas trocas:
   - **Nomes:**
     - `Filiais` → `Acessórios`;
     - `filiais` → `acessorios`;
     - `filial` → `acessorio`;
     - nas mensagens: "Acessório cadastrado/alterado/excluído com sucesso.", "Excluir o acessório..." e "Nenhum acessório cadastrado.".
   - **Coluna:** `<th>Cidade</th>` passa a ser `<th>Diária</th>`, e o `<td>` correspondente vira:
     ```html
     <td class="text-nowrap">{{ fmt.moeda(acessorio.diaria) }}</td>
     ```
   - **Campo do formulário:** o label e o input de cidade viram:
     ```html
     <label class="form-label" for="diaria">Valor da diária (R$)</label>
     <input id="diaria" type="number" step="0.01" min="0.01" class="form-control" v-model.number="form.diaria" required>
     ```
   - **`novo()` e `salvar()`:**
     ```js
     this.form = { id: null, nome: '', diaria: '' };
     ```
     ```js
     const corpo = { nome: this.form.nome, diaria: this.form.diaria };
     ```
   - Se não fez a questão 4, crie também o `fmt.moeda` em `app.js` (gabarito da questão 4).

**Testes:**

1. `backend/tests/dados.py`:
   ```python
   def corpo_acessorio(**campos) -> dict:
       return {"nome": "Cadeirinha de bebê", "diaria": 25.0, **campos}
   ```
2. `backend/tests/test_acessorios.py`, um arquivo novo:
   ```python
   from dados import corpo_acessorio


   def test_cadastrar_listar_alterar_excluir(client, funcionario):
       h = funcionario.headers
       r = client.post("/acessorios", json=corpo_acessorio(), headers=h)
       assert r.status_code == 201
       acessorio = r.json()
       assert acessorio == {"id": 1, "nome": "Cadeirinha de bebê", "diaria": 25.0}

       assert client.get("/acessorios", headers=h).json() == [acessorio]

       r = client.patch(f"/acessorios/{acessorio['id']}", json=corpo_acessorio(diaria=30.5), headers=h)
       assert r.json()["diaria"] == 30.5

       assert client.delete(f"/acessorios/{acessorio['id']}", headers=h).status_code == 204
       assert client.get(f"/acessorios/{acessorio['id']}", headers=h).status_code == 404


   def test_nome_unico(client, funcionario):
       h = funcionario.headers
       client.post("/acessorios", json=corpo_acessorio(), headers=h)
       gps = client.post("/acessorios", json=corpo_acessorio(nome="GPS"), headers=h).json()

       r = client.post("/acessorios", json=corpo_acessorio(), headers=h)
       assert r.status_code == 409
       assert r.json() == {"detail": "Já existe um acessório com este nome"}

       # alterar para o nome de outro também é barrado; manter o próprio nome não
       assert client.patch(f"/acessorios/{gps['id']}", json=corpo_acessorio(), headers=h).status_code == 409
       assert client.patch(f"/acessorios/{gps['id']}", json=corpo_acessorio(nome="GPS", diaria=9.9), headers=h).status_code == 200


   def test_campos_obrigatorios(client, funcionario):
       for corpo in ({"nome": "   ", "diaria": 10}, {"nome": "GPS", "diaria": 0}, {"nome": "GPS"}):
           assert client.post("/acessorios", json=corpo, headers=funcionario.headers).status_code == 422


   def test_so_funcionario_acessa(client, cliente):
       assert client.get("/acessorios").status_code == 401
       assert client.get("/acessorios", headers=cliente.headers).status_code == 403
   ```
3. `frontend/tests/frontend.test.js`:
   - em `PERFIS`:
     ```js
     'acessorios.html': ["'FUNCIONARIO'"],
     ```
   - no teste "menu: cada perfil vê...", na lista do funcionário:
     ```js
     assert.deepEqual(para('FUNCIONARIO'), ['Acessórios', 'Gerenciar Locações', 'Meus Dados', 'Veículos']);
     ```
</details>

---

## No fim

- **Testes:** depois da prova, todos passam, exceto o `test_insomnia.py`. Ele falha por causa da diária da questão 4, e isso é esperado: a coleção da Parte I não manda esse campo.
- **Passou das 2 horas?** Veja em qual questão perdeu mais tempo e refaça só ela numa cópia nova, sem olhar o gabarito.
- **Limpeza:** apague a pasta `simulado-ocar`.
