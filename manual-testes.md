# Roteiro de testes manuais – Parte I

Roteiro para conferir à mão tudo o que a banca avalia na Parte I: primeiro a API pelo Insomnia, depois o
front-end no navegador. Marque cada item conforme for testando. As mensagens entre aspas são exatamente as
que o sistema mostra.

Tempo estimado: ~15 min para a API (parte A) e ~20 min para o front (parte B).

---

## 0. Preparação

- [ ] Pare o back-end (se estiver rodando) e apague `backend/ocar.db`, para começar com o banco vazio.
- [ ] Terminal 1: `cd backend && source .venv/bin/activate && uvicorn app.main:app --port 8080 --reload`
- [ ] Terminal 2 (na raiz): `python3 frontend/servidor.py`
- [ ] No Insomnia, importe `Aproveitamento_de_Estudo_Avaliacao_Pratica_Parte_I.yaml`.
- [ ] Abra o **Base Environment** da coleção. É ali que ficam `token_cliente`, `token_funcionario`, ids, placa etc.

> Alternativa ao Insomnia: o Swagger em http://localhost:8080/docs (botão **Authorize** para colar o token).

---

## A. API pelo Insomnia

### A.1 Usuários e autenticação

- [ ] **Cadastrar - Cliente** → `201` com `{"id": 1, "login": "cliente", "perfil": "CLIENTE"}`. A resposta **não** traz a senha.
- [ ] **Cadastrar - Funcionario** → `201` com `id: 2` e `perfil: "FUNCIONARIO"`.
- [ ] **Cadastrar - Cliente** de novo → `409` "Já existe um usuário com este login" **(R01)**.
- [ ] **Verificar existencia de usuario** → `true`. Troque o login na URL por `ninguem` → `false`.
- [ ] **Login - Cliente** → `200` com `{"token": "..."}`. Copie o token para `token_cliente` no Base Environment.
- [ ] **Login - Funcionario** → copie o token para `token_funcionario`.
- [ ] Login com senha errada: troque `senha_cliente` para `x` e envie **Login - Cliente** → `401` "Login ou senha inválidos". Volte `senha_cliente` para `cliente`.
- [ ] **Meus dados - Cliente** → `200` com os dados do cliente (id 1).
- [ ] **Meus dados - Funcionario** → `200` com os dados do funcionário (id 2).
- [ ] **Listar clientes - Funcionario** → lista só com o cliente (o funcionário não aparece).

### A.2 Veículos

- [ ] **Cadastrar veiculo - Funcionario** → `201` com `"disponivel": true` **(R03)**.
- [ ] Envie de novo → `409` "Já existe um veículo com esta placa" **(R02)**.
- [ ] Segundo veículo (a coleção exclui o id 2): no Base Environment troque `placa` para `XYZ9A99`, envie **Cadastrar veiculo** → `id: 2`. Volte `placa` para `ABC1D23`.
- [ ] **Listar veiculos - Funcionario** → 2 veículos.
- [ ] **Consultar veiculo por ID - Cliente** → `200` (o cliente pode consultar por id).
- [ ] **Consultar veiculo por ID - Funcionario** → `200`.
- [ ] **Verificar existencia por placa - Funcionario** → `true`.
- [ ] **Alterar descricao - Funcionario** → `200`: a descrição muda para "Toyota Corolla XEi" e a placa continua `ABC1D23`.
- [ ] Na mesma requisição, acrescente `"placa": "ZZZ9999"` no corpo e envie → a placa **não** muda **(R02)**.
- [ ] **Excluir veiculo - Funcionario** (id 2) → `204`. Envie de novo → `404` "Veículo não encontrado".

### A.3 Locações

- [ ] **Criar locacao - Funcionario** → `201` com `"situacao": "EM_ANDAMENTO"` **(R06)**, `"clienteId": 1` e `"funcionarioId": 2`. O funcionário veio do token **(R04)**.
- [ ] **Consultar veiculo por ID** (veículo 1) → `"disponivel": false` **(R05)**.
- [ ] **Criar locacao** de novo → `409` "Veículo não está disponível" **(R05)**.
- [ ] No Base Environment troque `cliente_id` para `2` (o funcionário) e envie **Criar locacao** → `400` "O usuário informado não possui perfil CLIENTE" **(R04)**. Volte `cliente_id` para `1`.
- [ ] **Minhas locacoes - Cliente** → lista com a locação 1 **(R07)**.
- [ ] **Minhas locacoes - Funcionario** → lista com a locação 1 **(R07)**.
- [ ] **Consultar locacao por ID - Cliente** e **- Funcionario** → `200`.
- [ ] Troque `veiculo_exclusao_id` para `1` e envie **Excluir veiculo** → `409` "Veículo associado a locações não pode ser excluído" **(R09)**.
- [ ] **Finalizar locacao - Funcionario** → `200` com `"situacao": "FINALIZADA"`. Consulte o veículo 1 → `"disponivel": true` **(R08)**.
- [ ] **Finalizar locacao** de novo → `409` "Somente locações em andamento podem ser finalizadas" **(R08)**.
- [ ] **Excluir veiculo** (id 1) de novo → continua `409`: veículo com locação finalizada também não pode ser excluído **(R09)**.

### A.4 Senha

- [ ] **Alterar senha - Cliente** → `204`.
- [ ] **Login - Cliente** (com a senha antiga) → `401`. Troque `senha_cliente` para `123456` → `200`.
- [ ] **Alterar senha - Funcionario** → `204`. Troque `senha_funcionario` para `123456` e faça login de novo.

### A.5 Controle de acesso (tabela "Configurações de Acesso")

Copie o valor de `token_cliente` para `token_funcionario` para simular um cliente nas rotas de funcionário:

- [ ] **Listar clientes** → `403` "Acesso negado para o seu perfil".
- [ ] **Listar veiculos** → `403`.
- [ ] **Verificar existencia por placa** → `403`.
- [ ] **Cadastrar veiculo**, **Alterar descricao**, **Excluir veiculo** → `403`.
- [ ] **Criar locacao** e **Finalizar locacao** → `403`.
- [ ] Faça login de novo como funcionário e restaure o `token_funcionario` correto.
- [ ] Apague o valor de `token_cliente` (deixe vazio) e envie **Meus dados - Cliente** → `401` "Token não informado".
- [ ] Coloque `abc` em `token_cliente` → `401` "Token inválido ou expirado".
- [ ] As rotas públicas (**Cadastrar**, **Verificar existencia de usuario**, **Login**) funcionam sem token.

### A.6 Extras (opcional)

- [ ] **Outro cliente não vê a locação (R07):**
  - troque `login_cliente` para `ana`, envie **Cadastrar - Cliente** e **Login - Cliente**, e copie o token;
  - **Consultar locacao por ID - Cliente** → `403` "Você não tem acesso a esta locação";
  - **Minhas locacoes - Cliente** → `[]`.
- [ ] **Outro funcionário não finaliza (R08):**
  - crie uma locação nova em andamento com o funcionário 1;
  - cadastre e logue um segundo funcionário e use o token dele em **Finalizar locacao** → `403` "Apenas o funcionário responsável pode finalizar esta locação".
- [ ] **Campos obrigatórios:** em **Cadastrar veiculo** envie `"descricao": ""` ou `"   "` → `422`.
- [ ] **Recurso inexistente:** troque `locacao_id` para `99` e envie **Consultar locacao por ID** → `404` "Locação não encontrada".

---

## B. Front-end no navegador

Comece com o banco vazio de novo (passo 0). Use **duas janelas**: uma normal para o funcionário e uma
**anônima** para o cliente. Cada janela guarda a sua própria sessão, então dá para ficar logado com os dois.

### B.1 Cadastro e login

- [ ] Abra http://localhost:5500 → vai para a tela de login (logo OCar).
- [ ] **Cadastrar** → tela "Registro de usuários" com Login, Senha e Perfil.
- [ ] Cadastre `maria` como **Cliente** → volta ao login com "Usuário cadastrado com sucesso! Faça o login." e o login já preenchido.
- [ ] Cadastre `José` como **Funcionário**.
- [ ] Na tela de cadastro, digite `maria` e saia do campo → aparece "Este login já está em uso." e o botão Cadastrar fica desabilitado **(R01)**.
- [ ] Login com senha errada → "Login ou senha inválidos".
- [ ] Deixe login ou senha em branco → o navegador não deixa enviar (campos obrigatórios).

### B.2 Funcionário (janela normal, login `José`)

**Menu**
- [ ] Aparecem **Meus Dados**, **Veículos** e **Gerenciar Locações**.
- [ ] O rodapé mostra "Funcionário: José".

**Meus Dados**
- [ ] Login e Perfil ("Funcionário") aparecem só para leitura.
- [ ] Alterar senha com confirmação diferente → "As senhas não conferem."
- [ ] Alterar senha com confirmação igual → "Senha alterada com sucesso."
- [ ] Sair e entrar com a senha nova funciona.

**Veículos**
- [ ] Com o banco vazio aparece "Nenhum veículo cadastrado."
- [ ] Cadastrar: o campo Disponível mostra "Sim" e não é editável **(R03)**.
- [ ] Salvar sem descrição ou sem placa → o navegador não deixa.
- [ ] Cadastre "Fiat Toro - Completo" / `ABC-1234` → "Veículo cadastrado com sucesso." e a tabela atualiza.
- [ ] Cadastre um segundo veículo (ex.: "Renault Kwid" / `JKL-0M12`).
- [ ] Novo cadastro com placa `ABC-1234`: ao sair do campo aparece "Já existe um veículo com esta placa." e o Salvar fica desabilitado **(R02)**.
- [ ] Editar: a placa fica bloqueada e só a descrição muda **(R02)** → "Veículo alterado com sucesso."
- [ ] Excluir o Kwid → pede confirmação → "Veículo excluído com sucesso." e some da tabela.

**Gerenciar Locações**
- [ ] Com o banco vazio aparece "Nenhuma locação cadastrada."
- [ ] Nova locação:
  - o select de Veículo mostra só os disponíveis;
  - o select de Cliente mostra só clientes (`maria`, sem `José`);
  - Situação mostra "Em andamento" e não é editável.
- [ ] Salvar → "Locação cadastrada com sucesso.": a tabela mostra `maria` | `ABC-1234` | **Em andamento** **(R06)**.
- [ ] Em **Veículos**, o Fiat Toro agora está "Não" **(R05)**.
- [ ] Tente excluir o Fiat Toro → "Veículo associado a locações não pode ser excluído" **(R09)**.
- [ ] Nova locação de novo: o Fiat Toro não aparece. Sem outros veículos aparece "Nenhum veículo disponível no momento."
- [ ] **Gerenciar** na locação: veículo e cliente bloqueados, botão **Finalizar**.
- [ ] Finalizar → confirma → "Locação finalizada com sucesso." e a situação vira **Finalizada** **(R08)**.
- [ ] Em **Veículos**, o Fiat Toro volta a "Sim" **(R08)**.
- [ ] Gerenciar a locação finalizada → não aparece o botão Finalizar.
- [ ] Crie outra locação para o Fiat Toro: ele pode ser locado de novo.

### B.3 Cliente (janela anônima, login `maria`)

- [ ] O menu mostra só **Meus Dados** e **Minhas Locações**, e o rodapé mostra "Cliente: maria".
- [ ] **Minhas Locações** lista as locações dela com placa, descrição e situação **(R07)**.
- [ ] Na janela do funcionário, finalize uma locação. Na janela do cliente dê F5: a situação atualiza.
- [ ] **Meus Dados**: login `maria`, perfil "Cliente"; alterar senha funciona.

### B.4 Controle de acesso pelo endereço

- [ ] Como cliente, digite http://localhost:5500/veiculos.html → volta para o menu.
- [ ] Como cliente, digite http://localhost:5500/gerenciarlocacoes.html → volta para o menu.
- [ ] Como funcionário, digite http://localhost:5500/minhaslocacoes.html → volta para o menu.
- [ ] Clique em **Sair** → tela de login. Digite http://localhost:5500/menu.html → volta para o login.
- [ ] Depois de sair, o botão Voltar do navegador não mostra dados (redireciona para o login).

### B.5 Situações de erro

- [ ] **Back-end fora do ar:** pare o uvicorn (Ctrl+C) e abra **Meus Dados** → "Não foi possível conectar ao servidor. O back-end está rodando?" Suba o back-end de novo.
- [ ] **Banco recriado com a sessão aberta:** apague `backend/ocar.db`, reinicie o back-end e dê F5 em **Meus Dados** ou **Veículos** → volta para o login (o token antigo não vale mais).
- [ ] **Injeção de HTML:** cadastre um veículo com descrição `<b>teste</b>` → aparece o texto literal, sem negrito.

### B.6 Responsividade

Abra o F12 e clique no ícone de celular (Cmd+Shift+M no Mac). Teste em iPhone SE (375px), num celular maior e no iPad:

- [ ] Login e cadastro centralizados, sem rolagem horizontal.
- [ ] Menu com os cards em 2 colunas.
- [ ] Tabelas de Veículos e Gerenciar Locações cabem na tela, com os botões de ação visíveis (em Veículos, só os ícones).
- [ ] Formulários com um campo por linha.
- [ ] Cabeçalho com logo e Sair, e rodapé com o usuário, em todas as telas.

---

## C. Testes automáticos (1 minuto)

- [ ] `cd backend && .venv/bin/pytest` → todos passando (186 nesta versão).
- [ ] Na raiz: `node --test frontend/tests/frontend.test.js` → todos passando (39 nesta versão).

---

## Critérios de avaliação × roteiro

| Critério da banca | Onde conferir |
|---|---|
| Back-end organizado em camadas | README (Arquitetura) e `backend/tests/test_camadas.py` |
| Endpoints da API REST (coleção do Insomnia) | A.1 a A.4 |
| Operações de CRUD | A.2 (veículos), A.3 (locações), A.1 (usuários) |
| Autenticação e controle de acesso | A.1 (login), A.5, A.6 |
| Cadastro e autenticação de usuários (front) | B.1 |
| Gerenciamento de veículos e locações | B.2 |
| Integração com o back-end e atualização dos dados | B.2 e B.3 (tabelas atualizam depois de salvar, editar, excluir e finalizar) |
| Usabilidade e responsividade | B.4, B.5 e B.6 |
