# Dicas

## Como rodar

```bash
# Terminal 1 – back-end (porta 8080)
cd backend && source .venv/bin/activate && uvicorn app.main:app --port 8080 --reload

# Terminal 2 – front-end (porta 5500), na raiz do projeto
python3 frontend/servidor.py
```

- Front: http://localhost:5500/login.html
- Swagger da API: http://localhost:8080/docs (funciona sem internet)
- Testes do back-end: `cd backend && .venv/bin/pytest` (≈2s)
- Testes do front-end: `node --test frontend/tests/frontend.test.js` (na raiz do projeto)

## Antes da avaliação com o Insomnia

- Comece com o banco vazio: pare o back-end, apague `backend/ocar.db` e suba de novo. A coleção espera os ids começando em 1 (cliente = 1, funcionário = 2, veículo = 1, locação = 1).
- Rode na ordem: cadastrar cliente e funcionário, fazer login com os dois e copiar os tokens para `token_cliente` e `token_funcionario` no Base Environment.
- A coleção só cadastra um veículo, mas "Excluir veiculo" usa `veiculo_exclusao_id = 2`. Antes de excluir, cadastre um segundo veículo, sem locação.
- Cadastre o veículo antes de "Consultar veiculo por ID" e de "Criar locacao", senão a resposta é 404.
- Depois de "Alterar senha", o token antigo continua válido. Para fazer login de novo, atualize `senha_cliente`/`senha_funcionario` com a `nova_senha`.

## Durante a Parte II

- O [`guia-alteracoes.md`](guia-alteracoes.md) tem o passo a passo de cada tipo de alteração, com código pronto e uma explicação do Vue para quem sabe Python.
- A seção "Onde mexer" do `README.md` diz onde alterar para cada tipo de pedido (campo novo, regra, endpoint, permissão, tela nova) e tem um exemplo completo com o campo `cor`.
- Alterou uma entity (campo novo)? Apague `backend/ocar.db` e reinicie. Não há migração: as tabelas são recriadas do zero.
- Com o `--reload`, o back-end reinicia sozinho a cada alteração em `.py`.
- No front basta salvar e dar F5: o `servidor.py` desliga o cache, então o JS/CSS novo sempre é carregado.
- Erros de JavaScript e avisos do Vue aparecem no console do navegador (F12).
- No back-end, as rotas fixas (`/existe`, `/minhas`) precisam vir antes das rotas com `/{id}` no controller.
- Para uma regra nova, use `raise NegocioException("mensagem")` (400) no service, ou `ConflitoException` (409), `NaoEncontradoException` (404), `AcessoNegadoException` (403). A mensagem aparece sozinha no alerta da página.
- O controller nunca recebe a entidade `Usuario`: recebe `UsuarioLogado` e passa `usuario.id` (e `usuario.perfil`, se precisar) ao service. O `test_camadas.py` falha se um controller importar entidade ou repository.
- O teste do front compila o template e o `<script>` de cada página. Vírgula esquecida, tag sem fechar ou `{{ }}` quebrado aparecem como falha, com o arquivo e a linha, sem precisar abrir o navegador.
- Rode os testes depois de cada mudança. Os que falharem na parte que você mexeu são esperados quando o professor muda o enunciado (modelo, DTOs, menu): atualize o teste. Os que falharem em outra parte apontam algo que quebrou sem querer.
- Campo novo obrigatório: inclua-o no corpo padrão em `backend/tests/dados.py` e nas listas de `test_modelo.py`. Com isso só o `test_insomnia.py` continua falhando, porque a coleção da Parte I não envia o campo.

## IA na Parte II (com e sem internet)

Antes de tudo, confirme com o professor se o uso de IA é permitido.

**Com internet:** o Claude Code normal, na pasta do projeto.

```bash
claude
```

**Sem internet:** o mesmo Claude Code, usando um modelo que roda no notebook (Ollama). Abra dois terminais:

```bash
# Terminal A: servidor do Ollama (deixe aberto). Sem o OLLAMA_CONTEXT_LENGTH ele usa 4k de contexto e o Claude Code não funciona
OLLAMA_CONTEXT_LENGTH=65536 ollama serve

# Terminal B: na pasta do projeto
CLAUDE_CODE_MAX_CONTEXT_TOKENS=65536 CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 ollama launch claude --model qwen3.5:9b
```

- **Vale só para essa janela do terminal.** O `ollama launch` não altera a configuração do Claude Code, então o `claude` normal continua usando sua conta. Conferido comparando os arquivos de configuração antes e depois.
- **`CLAUDE_CODE_MAX_CONTEXT_TOKENS`:** diz ao Claude Code o tamanho real do contexto do modelo. Sem ele, o Claude Code supõe 200k e a conversa pode passar do limite.
- **`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`:** evita que ele tente acessar a internet para telemetria e atualização.
- **Se o `ollama serve` disser que o endereço já está em uso**, o servidor já está rodando. Só confira se foi iniciado com o `OLLAMA_CONTEXT_LENGTH`.
- **Para só tirar dúvidas, sem mexer em arquivos:** `ollama run qwen3.5:9b` (ou `gpt-oss:20b`) abre um chat no terminal. Para sair, `/bye`.

Resultado dos modelos instalados, testados em 16/10/2026 numa cópia do projeto, pedindo a receita 3.3 do `guia-alteracoes.md` (campo `cor`):

| Modelo        | Tamanho | Alterando arquivos                                                                                                          | Como chat de dúvidas            |
|---------------|---------|-----------------------------------------------------------------------------------------------------------------------------|---------------------------------|
| `qwen3.5:9b`  | 6,6 GB  | **O melhor.** Alterou os 6 arquivos certos em ~10 min. Deixou um erro pequeno no HTML (`:value` junto com `v-model`), que o teste do front pega. | resposta certa em ~2s  |
| `gpt-oss:20b` | 13 GB   | Fraco como agente. Na 1ª tentativa só explicou, não editou nada e **inventou** o resultado dos testes. Na 2ª, com instruções detalhadas, fez 5 de 6 arquivos e esqueceu a coluna da tabela (~6 min). | resposta certa em ~10s |

**O que esperar:**
- Os dois são bem mais fracos e lentos que o Claude Code com internet.
- Com o guia, a mesma alteração leva uns 5 a 10 minutos à mão, ou seja, o modelo local não é mais rápido.
- Ele ajuda mais a tirar dúvidas de Vue e a fazer mudanças repetitivas, sempre conferidas.

**Como pedir (o que funcionou melhor):**
- Cite a receita do guia e liste os arquivos. Por exemplo: "Siga a receita 3.3 do guia-alteracoes.md para adicionar o campo X. Faça cada alteração com a ferramenta Edit, um arquivo por vez: (arquivos). Não explique."
- Um pedido por vez. Depois, rode os testes você mesmo e confira no navegador.
- **Não confie no "pronto":** o modelo pode dizer que fez algo que não fez. Nos testes, aconteceu de afirmar alterações que não existiam e de errar uma pergunta simples sobre o menu.
- **Recuse se ele pedir para rodar `git add`/`git commit`.** O `gpt-oss` tentou fazer commit sozinho no teste.
- **Antes de um pedido grande, faça uma cópia da pasta**, por exemplo `cp -R aproveitamento-ds aproveitamento-ds-copia`. Os arquivos não estão commitados, então o git não desfaz as mudanças.

**Ensaio sem internet (faça antes da prova):**
1. Desligue o Wi-Fi.
2. Suba o back e o front. Abra http://localhost:5500/login.html e http://localhost:8080/docs.
3. Abra os terminais A e B acima, peça uma alteração do guia e rode os testes.
4. Abra o Insomnia. Ele não estava instalado em `/Applications`: instale antes e confirme que abre sem pedir login.

O teste sem internet foi simulado com um proxy inexistente para tudo que não fosse `localhost`, e o Claude Code com o modelo local funcionou. Com o Wi-Fi realmente desligado, ainda não foi testado.

## O que não foi testado

- A coleção roda no `test_insomnia.py`, que lê o YAML e faz as requisições, e também foi executada contra o servidor real. Não foi importada no aplicativo Insomnia. Vale importar e rodar uma vez antes da avaliação.
- Os diálogos `confirm()` de "Excluir veículo" e "Finalizar locação" foram simulados no teste. Vale clicar uma vez de verdade.
- A responsividade foi testada com as páginas em iframes de 375px, não com o DevTools ou um celular de verdade. Vale conferir no modo responsivo do Chrome (F12 → ícone de celular).
- Não foi possível confirmar pelo console que não há avisos do Vue. Abra o F12 e confira.
- Na segunda rodada de testes no navegador, a janela do Chrome estava em segundo plano e os cliques por coordenada não chegavam. Os cenários de erro foram exercitados disparando eventos direto nos elementos da página (cliques e digitação via JavaScript). A primeira rodada, com o caminho feliz, usou cliques reais.
- Não há tratamento de concorrência para dois funcionários locando o mesmo veículo no mesmo instante. Login e placa duplicados ao mesmo tempo são barrados pelo banco (409).

## Observações técnicas

- O `HTTPServer` do Python consulta o DNS ao iniciar (`getfqdn`), o que levava cerca de 27s neste Mac. Por isso o `frontend/servidor.py` usa `ThreadingTCPServer`.
- O PyYAML está no `requirements.txt` (seção de testes) porque o `test_insomnia.py` lê a coleção.
- Os testes usam um banco próprio (`backend/tests/test_ocar.db`, apagado no fim) e `BCRYPT_ROUNDS=4` para rodar rápido. O `ocar.db` de uso normal não é tocado.
- Botão Voltar depois de Sair: o Chrome restaura a página do cache sem recarregar. O `criarApp` (em `js/app.js`) confere a sessão de novo nesse caso e manda para o login. Sem isso, a tela anterior aparecia com os dados.
- O `/docs` padrão do FastAPI baixa o Swagger da internet (cdn.jsdelivr.net) e fica em branco sem conexão. Por isso o `main.py` serve o Swagger com os arquivos de `backend/static/swagger-ui/` (versão 5.32.15), e o `test_documentacao.py` confere que a página não busca nada de fora. O `/redoc` foi desligado pelo mesmo motivo.
- O `ocar.db` é sempre criado em `backend/`, de onde quer que o uvicorn seja iniciado.
- O `*.db` está no `.gitignore`, então o banco local não vai para o repositório.
