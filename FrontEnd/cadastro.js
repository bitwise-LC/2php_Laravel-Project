function mascara_cpf() {
  const campo = document.getElementById("cpf");
  campo.value = campo.value.replace(/\D/g, "").replace(/(\d{3})(\d)/, "$1.$2").replace(/(\d{3})(\d)/, "$1.$2").replace(/(\d{3})(\d{1,2})$/, "$1-$2");
}

function mascara_telefone() {
  const campo = document.getElementById("telefone");
  campo.value = campo.value.replace(/\D/g, "").replace(/^(\d{2})(\d)/, "($1) $2").replace(/(\d{5})(\d)/, "$1-$2");
}

document.getElementById("cadastro-container")?.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  const formulario = evento.currentTarget;
  const botao = formulario.querySelector("button[type=submit]");
  botao.disabled = true;
  try {
    const dados = await PrazoAPI.request("/organizacoes", {
      method: "POST",
      body: JSON.stringify({
        empresa: document.getElementById("empresa").value,
        nome: document.getElementById("responsavel").value,
        cpf: document.getElementById("cpf").value,
        telefone: document.getElementById("telefone").value,
        email: document.getElementById("email").value,
        senha: document.getElementById("senha").value
      })
    });
    PrazoAPI.salvarSessao({ id_usuario: dados.usuario.id_usuario, id_loja: dados.loja.id_loja, nome: dados.funcionario.nome_completo });
    window.location.href = "dashboard.html";
  } catch (erro) { alert(erro.message); }
  finally { botao.disabled = false; }
});
