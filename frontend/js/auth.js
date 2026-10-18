// Sessão do usuário: o token JWT fica no localStorage e os dados (id, login, perfil) são lidos do próprio token.
const auth = {
  salvarToken(token) {
    localStorage.setItem('token', token);
  },

  token() {
    return localStorage.getItem('token');
  },

  // Retorna { id, login, perfil } ou null se não estiver logado / token expirado
  usuario() {
    const token = this.token();
    if (!token) return null;
    try {
      const payload = JSON.parse(decodificarBase64Url(token.split('.')[1]));
      if (payload.exp * 1000 < Date.now()) return null;
      return { id: Number(payload.sub), login: payload.login, perfil: payload.perfil };
    } catch {
      return null;
    }
  },

  // Sem login -> login.html; perfil não permitido -> menu.html
  exigir(...perfis) {
    const usuario = this.usuario();
    if (!usuario) {
      this.sair();
      return null;
    }
    if (perfis.length && !perfis.includes(usuario.perfil)) {
      window.location.href = 'menu.html';
      return null;
    }
    return usuario;
  },

  sair() {
    localStorage.removeItem('token');
    window.location.href = 'login.html';
  },
};

function decodificarBase64Url(texto) {
  const base64 = texto.replace(/-/g, '+').replace(/_/g, '/');
  const bytes = Uint8Array.from(atob(base64), (c) => c.charCodeAt(0));
  return new TextDecoder().decode(bytes);
}
