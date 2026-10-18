// Testes do front-end (sem npm): node --test frontend/tests/
const { test, describe } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const FRONT = path.join(__dirname, '..');

// Carrega auth.js, api.js e app.js como o navegador faria, com window/localStorage/fetch/Vue falsos
function carregar({ fetch, token } = {}) {
  const armazenamento = new Map(token ? [['token', token]] : []);
  const criados = [];
  const eventos = {};
  const contexto = {
    window: {
      location: { href: 'pagina-atual.html', search: '' },
      addEventListener: (nome, funcao) => (eventos[nome] = funcao),
    },
    localStorage: {
      getItem: (k) => (armazenamento.has(k) ? armazenamento.get(k) : null),
      setItem: (k, v) => armazenamento.set(k, String(v)),
      removeItem: (k) => armazenamento.delete(k),
    },
    fetch,
    atob,
    TextDecoder,
    console,
    setTimeout: (funcao) => funcao(), // executa na hora para o teste ficar determinístico
    Vue: {
      createApp(opcoes) {
        const app = { opcoes, componentes: {}, config: { globalProperties: {} } };
        app.component = (nome, def) => (app.componentes[nome] = def);
        criados.push(app);
        return app;
      },
    },
  };
  vm.createContext(contexto);
  const codigo = ['auth.js', 'api.js', 'app.js']
    .map((f) => fs.readFileSync(path.join(FRONT, 'js', f), 'utf8'))
    .join('\n');
  const globais = vm.runInContext(`${codigo}\n;({ auth, api, fmt, criarApp, mensagemDeErro, API_URL })`, contexto);
  return { ...globais, contexto, armazenamento, criados, eventos };
}

function jwt(payload) {
  const parte = (obj) => Buffer.from(JSON.stringify(obj)).toString('base64url');
  return `${parte({ alg: 'HS256', typ: 'JWT' })}.${parte(payload)}.assinatura`;
}

const daquiUmaHora = () => Math.floor(Date.now() / 1000) + 3600;
const tokenDe = (perfil, login = 'José') => jwt({ sub: '2', login, perfil, exp: daquiUmaHora() });

function resposta(status, corpo) {
  const texto = corpo === undefined ? '' : typeof corpo === 'string' ? corpo : JSON.stringify(corpo);
  return { ok: status >= 200 && status < 300, status, text: async () => texto };
}

describe('auth', () => {
  test('sem token não há usuário', () => {
    const { auth } = carregar();
    assert.equal(auth.usuario(), null);
  });

  test('lê id, login (com acento) e perfil do JWT', () => {
    const { auth } = carregar({ token: tokenDe('FUNCIONARIO') });
    assert.deepEqual({ ...auth.usuario() }, { id: 2, login: 'José', perfil: 'FUNCIONARIO' });
  });

  test('token expirado conta como deslogado', () => {
    const { auth } = carregar({ token: jwt({ sub: '1', login: 'a', perfil: 'CLIENTE', exp: 1000 }) });
    assert.equal(auth.usuario(), null);
  });

  for (const lixo of ['abc', 'a.b.c', 'a.###.c', `x.${Buffer.from('não é json').toString('base64url')}.y`]) {
    test(`token malformado (${lixo.slice(0, 12)}) conta como deslogado`, () => {
      const { auth } = carregar({ token: lixo });
      assert.equal(auth.usuario(), null);
    });
  }

  test('exigir sem login manda para o login e limpa o token', () => {
    const { auth, contexto, armazenamento } = carregar({ token: 'lixo' });
    assert.equal(auth.exigir('CLIENTE'), null);
    assert.equal(contexto.window.location.href, 'login.html');
    assert.equal(armazenamento.has('token'), false);
  });

  test('exigir com perfil errado manda para o menu', () => {
    const { auth, contexto } = carregar({ token: tokenDe('CLIENTE') });
    assert.equal(auth.exigir('FUNCIONARIO'), null);
    assert.equal(contexto.window.location.href, 'menu.html');
  });

  test('exigir com perfil certo devolve o usuário e não redireciona', () => {
    const { auth, contexto } = carregar({ token: tokenDe('CLIENTE') });
    assert.equal(auth.exigir('CLIENTE', 'FUNCIONARIO').perfil, 'CLIENTE');
    assert.equal(contexto.window.location.href, 'pagina-atual.html');
  });

  test('sair apaga o token e volta ao login', () => {
    const { auth, contexto, armazenamento } = carregar({ token: tokenDe('CLIENTE') });
    auth.sair();
    assert.equal(armazenamento.has('token'), false);
    assert.equal(contexto.window.location.href, 'login.html');
  });
});

describe('api', () => {
  test('envia JSON, Bearer e usa a URL do back-end', async () => {
    const chamadas = [];
    const token = tokenDe('FUNCIONARIO');
    const { api, API_URL } = carregar({
      token,
      fetch: async (url, opcoes) => (chamadas.push({ url, opcoes }), resposta(201, { id: 1 })),
    });
    assert.deepEqual({ ...(await api.post('/veiculos', { placa: 'ABC' })) }, { id: 1 });
    assert.equal(API_URL, 'http://localhost:8080');
    assert.equal(chamadas[0].url, 'http://localhost:8080/veiculos');
    assert.equal(chamadas[0].opcoes.method, 'POST');
    assert.equal(chamadas[0].opcoes.body, '{"placa":"ABC"}');
    assert.equal(chamadas[0].opcoes.headers['Content-Type'], 'application/json');
    assert.equal(chamadas[0].opcoes.headers.Authorization, `Bearer ${token}`);
  });

  test('sem token não manda Authorization; GET sem corpo', async () => {
    let opcoesUsadas;
    const { api } = carregar({ fetch: async (url, opcoes) => ((opcoesUsadas = opcoes), resposta(200, true)) });
    assert.equal(await api.get('/usuarios/existe?login=a'), true);
    assert.equal(opcoesUsadas.headers.Authorization, undefined);
    assert.equal(opcoesUsadas.body, undefined);
  });

  test('métodos PATCH e DELETE; 204 devolve null', async () => {
    const metodos = [];
    const { api } = carregar({ fetch: async (url, opcoes) => (metodos.push(opcoes.method), resposta(204)) });
    assert.equal(await api.patch('/locacoes/1/finalizar'), null);
    assert.equal(await api.delete('/veiculos/1'), null);
    assert.deepEqual(metodos, ['PATCH', 'DELETE']);
  });

  test('erro de regra: mensagem do back-end', async () => {
    const { api } = carregar({ fetch: async () => resposta(409, { detail: 'Já existe um veículo com esta placa' }) });
    await assert.rejects(api.post('/veiculos', {}), { message: 'Já existe um veículo com esta placa' });
  });

  test('erro de validação (422): junta campo e mensagem', async () => {
    const detail = [
      { loc: ['body', 'placa'], msg: 'Field required' },
      { loc: ['body', 'descricao'], msg: 'String should have at least 1 character' },
    ];
    const { api } = carregar({ fetch: async () => resposta(422, { detail }) });
    await assert.rejects(api.post('/veiculos', {}), {
      message: 'placa: Field required; descricao: String should have at least 1 character',
    });
  });

  test('erro sem JSON (ex.: 500) mostra o status', async () => {
    const { api } = carregar({ fetch: async () => resposta(500, 'Internal Server Error') });
    await assert.rejects(api.get('/veiculos'), { message: 'Erro 500' });
  });

  test('back-end fora do ar', async () => {
    const { api } = carregar({ fetch: async () => { throw new TypeError('Failed to fetch'); } });
    await assert.rejects(api.get('/veiculos'), { message: /Não foi possível conectar ao servidor/ });
  });

  test('401 com token: desloga e volta ao login', async () => {
    const { api, contexto, armazenamento } = carregar({
      token: tokenDe('CLIENTE'),
      fetch: async () => resposta(401, { detail: 'Token inválido ou expirado' }),
    });
    await assert.rejects(api.get('/usuarios/meus-dados'), { message: 'Token inválido ou expirado' });
    assert.equal(armazenamento.has('token'), false);
    assert.equal(contexto.window.location.href, 'login.html');
  });

  test('401 no próprio login só mostra a mensagem', async () => {
    const { api, contexto } = carregar({
      token: tokenDe('CLIENTE'),
      fetch: async () => resposta(401, { detail: 'Login ou senha inválidos' }),
    });
    await assert.rejects(api.post('/login', {}), { message: 'Login ou senha inválidos' });
    assert.equal(contexto.window.location.href, 'pagina-atual.html');
  });
});

describe('app.js', () => {
  test('formatadores', () => {
    const { fmt } = carregar();
    assert.equal(fmt.perfil('CLIENTE'), 'Cliente');
    assert.equal(fmt.perfil('FUNCIONARIO'), 'Funcionário');
    assert.equal(fmt.situacao('EM_ANDAMENTO'), 'Em andamento');
    assert.equal(fmt.situacao('FINALIZADA'), 'Finalizada');
    assert.equal(fmt.simNao(true), 'Sim');
    assert.equal(fmt.simNao(false), 'Não');
    assert.equal(fmt.situacao('OUTRA'), 'OUTRA');
  });

  test('página protegida sem login não cria o app', () => {
    const { criarApp, criados, contexto } = carregar();
    const app = criarApp({ perfis: ['FUNCIONARIO'] });
    app.mount('#app'); // não pode quebrar
    assert.equal(criados.length, 0);
    assert.equal(contexto.window.location.href, 'login.html');
  });

  test('página protegida com login cria o app com cabeçalho, rodapé, fmt e usuário', () => {
    const { criarApp, criados } = carregar({ token: tokenDe('FUNCIONARIO') });
    criarApp({ perfis: ['FUNCIONARIO'] });
    assert.equal(criados.length, 1);
    assert.deepEqual(Object.keys(criados[0].componentes), ['app-header', 'app-footer']);
    assert.equal(criados[0].config.globalProperties.usuarioLogado.login, 'José');
    assert.equal(typeof criados[0].config.globalProperties.fmt.situacao, 'function');
  });

  test('botão Voltar depois de sair: página restaurada do cache confere a sessão de novo', () => {
    const { criarApp, eventos, contexto, armazenamento } = carregar({ token: tokenDe('FUNCIONARIO') });
    criarApp({ perfis: ['FUNCIONARIO'] });
    armazenamento.delete('token'); // usuário clicou em Sair em outra página
    eventos.pageshow({ persisted: true });
    assert.equal(contexto.window.location.href, 'login.html');
  });

  test('página restaurada do cache com sessão válida continua onde está', () => {
    const { criarApp, eventos, contexto } = carregar({ token: tokenDe('FUNCIONARIO') });
    criarApp({ perfis: ['FUNCIONARIO'] });
    eventos.pageshow({ persisted: true });
    assert.equal(contexto.window.location.href, 'pagina-atual.html');
  });

  test('página pública (sem perfis) cria o app mesmo deslogado', () => {
    const { criarApp, criados } = carregar();
    criarApp({});
    assert.equal(criados.length, 1);
  });
});

describe('páginas', () => {
  const paginas = fs.readdirSync(FRONT).filter((f) => f.endsWith('.html'));
  const ler = (pagina) => fs.readFileSync(path.join(FRONT, pagina), 'utf8');

  // perfis exigidos por página, conforme a tabela "Menu de Acesso" do enunciado
  const PERFIS = {
    'login.html': null,
    'usuario.html': null,
    'menu.html': ["'CLIENTE'", "'FUNCIONARIO'"],
    'meusdados.html': ["'CLIENTE'", "'FUNCIONARIO'"],
    'veiculos.html': ["'FUNCIONARIO'"],
    'gerenciarlocacoes.html': ["'FUNCIONARIO'"],
    'minhaslocacoes.html': ["'CLIENTE'"],
  };

  test('todas as telas do enunciado existem', () => {
    for (const pagina of [...Object.keys(PERFIS), 'index.html']) assert.ok(paginas.includes(pagina), pagina);
  });

  for (const [pagina, perfis] of Object.entries(PERFIS)) {
    test(`${pagina}: scripts na ordem, viewport, v-cloak e perfis`, () => {
      const html = ler(pagina);
      const scripts = [...html.matchAll(/<script src="([^"]+)"/g)].map((m) => m[1]);
      assert.deepEqual(scripts, ['vendor/vue.global.js', 'js/auth.js', 'js/api.js', 'js/app.js']);
      assert.match(html, /<meta name="viewport" content="width=device-width, initial-scale=1">/);
      assert.match(html, /<div id="app" v-cloak/);
      assert.match(html, /\.mount\('#app'\)/);
      const declarado = html.match(/perfis: \[([^\]]*)\],\n/);
      if (perfis === null) assert.equal(declarado, null);
      else assert.deepEqual(declarado[1].split(', '), perfis);
    });
  }

  test('todo arquivo local referenciado existe (src, href e url do menu)', () => {
    for (const pagina of paginas) {
      const html = ler(pagina);
      const refs = [
        ...[...html.matchAll(/\s(?:src|href)="([^"#:]+)"/g)].map((m) => m[1]),
        ...[...html.matchAll(/url: '([^']+)'/g)].map((m) => m[1]),
        ...[...html.matchAll(/location\.href = '([^'?]+)/g)].map((m) => m[1]),
      ];
      for (const ref of refs) assert.ok(fs.existsSync(path.join(FRONT, ref)), `${pagina} -> ${ref}`);
    }
  });

  test('menu: cada perfil vê exatamente as funcionalidades do enunciado', () => {
    const html = ler('menu.html');
    const itens = [...html.matchAll(/titulo: '([^']+)'.*perfis: \[([^\]]+)\]/g)].map((m) => [m[1], m[2]]);
    const para = (perfil) => itens.filter(([, p]) => p.includes(perfil)).map(([t]) => t).sort();
    assert.deepEqual(para('CLIENTE'), ['Meus Dados', 'Minhas Locações']);
    assert.deepEqual(para('FUNCIONARIO'), ['Gerenciar Locações', 'Meus Dados', 'Veículos']);
  });

  test('as páginas usam os endpoints certos da API', () => {
    const usos = {
      'login.html': ["api.post('/login'"],
      'usuario.html': ["api.post('/usuarios'", "api.get('/usuarios/existe?login="],
      'meusdados.html': ["api.get('/usuarios/meus-dados')", "api.patch('/usuarios/senha'"],
      'veiculos.html': ["api.get('/veiculos')", "api.post('/veiculos'", 'api.patch(`/veiculos/${', 'api.delete(`/veiculos/${', "api.get('/veiculos/existe?placa="],
      'gerenciarlocacoes.html': ["api.get('/locacoes/minhas')", "api.get('/usuarios/clientes')", "api.post('/locacoes'", 'api.patch(`/locacoes/${this.form.id}/finalizar`)'],
      'minhaslocacoes.html': ["api.get('/locacoes/minhas')", 'api.get(`/veiculos/${id}`)'],
    };
    for (const [pagina, trechos] of Object.entries(usos)) {
      for (const trecho of trechos) assert.ok(ler(pagina).includes(trecho), `${pagina} deveria chamar ${trecho}`);
    }
  });

  test('nenhuma página usa v-html (evita injeção de HTML)', () => {
    for (const pagina of paginas) assert.ok(!ler(pagina).includes('v-html'), pagina);
  });

  // Compilador do Vue de verdade (vendor/vue.global.js), usado só para checar a sintaxe dos templates
  function compiladorVue() {
    const contexto = { console: { ...console, info() {} } }; // info: aviso de "development build"
    vm.createContext(contexto);
    vm.runInContext(ler('vendor/vue.global.js'), contexto);
    return contexto.Vue;
  }

  test('template e <script> de cada página compilam (tag sem fechar, vírgula esquecida...)', () => {
    const Vue = compiladorVue();
    for (const pagina of paginas) {
      const html = ler(pagina);
      for (const m of html.matchAll(/<script>([\s\S]*?)<\/script>/g)) {
        const linha = html.slice(0, m.index).split('\n').length - 1;
        try {
          new vm.Script(m[1], { filename: pagina, lineOffset: linha });
        } catch (e) {
          assert.fail(`${e.stack.split('\n')[0]} -> ${e.message}`);
        }
      }
      const inicio = html.indexOf('<div id="app"');
      if (inicio === -1) continue;
      const erros = [];
      Vue.compile(html.slice(inicio, html.indexOf('<script src')), {
        onError: (e) => erros.push(e.message),
        onWarn: (e) => erros.push(e.message),
        decodeEntities: (texto) => texto,
      });
      assert.deepEqual(erros, [], `${pagina}: erro no template`);
    }
  });
});
