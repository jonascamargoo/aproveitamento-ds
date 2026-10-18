// Endereço do back-end
const API_URL = 'http://localhost:8080';

// Uso: await api.get('/veiculos'), await api.post('/veiculos', { placa, descricao }) ...
// Em caso de erro lança Error com a mensagem vinda do back-end (e.message).
const api = {
  async requisicao(metodo, caminho, corpo) {
    const headers = { 'Content-Type': 'application/json' };
    const token = auth.token();
    if (token) headers['Authorization'] = `Bearer ${token}`;

    let resposta;
    try {
      resposta = await fetch(API_URL + caminho, {
        method: metodo,
        headers,
        body: corpo === undefined ? undefined : JSON.stringify(corpo),
      });
    } catch {
      throw new Error('Não foi possível conectar ao servidor. O back-end está rodando?');
    }

    // Token inválido ou expirado: volta para o login
    if (resposta.status === 401 && token && caminho !== '/login') {
      auth.sair();
    }

    const texto = await resposta.text();
    let dados = null;
    try {
      dados = texto ? JSON.parse(texto) : null;
    } catch {
      dados = null;
    }

    if (!resposta.ok) {
      throw new Error(mensagemDeErro(dados) || `Erro ${resposta.status}`);
    }
    return dados;
  },

  get(caminho) {
    return this.requisicao('GET', caminho);
  },
  post(caminho, corpo) {
    return this.requisicao('POST', caminho, corpo);
  },
  patch(caminho, corpo) {
    return this.requisicao('PATCH', caminho, corpo);
  },
  delete(caminho) {
    return this.requisicao('DELETE', caminho);
  },
};

// O back-end responde {"detail": "mensagem"} ou, em erro de validação (422), {"detail": [{loc, msg}, ...]}
function mensagemDeErro(dados) {
  if (!dados || !dados.detail) return null;
  if (typeof dados.detail === 'string') return dados.detail;
  return dados.detail.map((e) => `${e.loc[e.loc.length - 1]}: ${e.msg}`).join('; ');
}
