// Formatadores usados nos templates: {{ fmt.situacao(locacao.situacao) }}
const fmt = {
  perfil: (perfil) => ({ CLIENTE: 'Cliente', FUNCIONARIO: 'Funcionário' })[perfil] || perfil,
  situacao: (situacao) => ({ EM_ANDAMENTO: 'Em andamento', FINALIZADA: 'Finalizada' })[situacao] || situacao,
  simNao: (valor) => (valor ? 'Sim' : 'Não'),
};

const AppHeader = {
  template: `
    <nav class="navbar bg-white border-bottom border-2 border-dark">
      <div class="container">
        <a class="navbar-brand fw-bold logo" href="menu.html"><i class="bi bi-car-front-fill"></i> OCar</a>
        <button class="btn btn-outline-secondary btn-sm" @click="sair" title="Sair">
          <i class="bi bi-box-arrow-right"></i> Sair
        </button>
      </div>
    </nav>`,
  methods: {
    sair() {
      auth.sair();
    },
  },
};

const AppFooter = {
  template: `
    <footer class="bg-white border-top border-2 border-dark py-2 mt-auto">
      <div class="container" v-if="usuarioLogado">
        {{ fmt.perfil(usuarioLogado.perfil) }}: <span class="text-danger fw-semibold">{{ usuarioLogado.login }}</span>
      </div>
    </footer>`,
};

// Cria o app Vue da página.
// opcoes.perfis: perfis que podem acessar a página (ex.: ['FUNCIONARIO']). Sem "perfis" a página é pública.
function criarApp(opcoes) {
  if (opcoes.perfis) {
    if (!auth.exigir(...opcoes.perfis)) {
      return { mount() {} }; // já foi redirecionado
    }
    // Botão Voltar depois de sair: o navegador restaura a página do cache sem recarregar,
    // então a sessão precisa ser conferida de novo
    window.addEventListener('pageshow', (evento) => {
      if (evento.persisted) setTimeout(() => auth.exigir(...opcoes.perfis));
    });
  }

  const app = Vue.createApp(opcoes);
  app.component('app-header', AppHeader);
  app.component('app-footer', AppFooter);
  app.config.globalProperties.fmt = fmt;
  app.config.globalProperties.usuarioLogado = auth.usuario();
  return app;
}
