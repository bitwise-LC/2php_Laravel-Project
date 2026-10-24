document.getElementById("login-form")?.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  const botao = evento.currentTarget.querySelector("button[type=submit]");
  botao.disabled = true;
  try {
    const sessao = await PrazoAPI.request("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email: document.getElementById("email").value, senha: document.getElementById("password").value })
    });
    PrazoAPI.salvarSessao(sessao);
    window.location.href = "dashboard.html";
  } catch (erro) { alert(erro.message); }
  finally { botao.disabled = false; }
});
