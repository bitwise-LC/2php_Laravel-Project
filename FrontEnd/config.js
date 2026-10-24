let perfilAtual;

function abrirAba(id, botao) {
  document.querySelectorAll(".pagina").forEach(p => p.classList.remove("ativo"));
  document.querySelectorAll(".aba").forEach(p => p.classList.remove("ativa"));
  document.getElementById(id).classList.add("ativo");
  botao.classList.add("ativa");
  if (id === "categorias") carregarCategorias();
}

async function carregarPerfil() {
  PrazoAPI.exigirSessao();
  perfilAtual = await PrazoAPI.request("/perfil");
  const f = perfilAtual.funcionario, e = perfilAtual.empresa;
  document.getElementById("nomeLoja").value = e.nome;
  document.getElementById("emailLoja").value = f.email;
  document.getElementById("telefoneLoja").value = e.telefones[0] || "";
  document.getElementById("nomeUsuario").value = f.nome_completo;
  document.getElementById("emailUsuario").value = f.email;
  document.getElementById("empresaUsuario").value = e.nome;
  document.getElementById("telefoneUsuario").value = f.telefones[0] || "";
  document.getElementById("cargoUsuario").value = f.cargo;
  document.getElementById("cpfUsuario").value = f.cpf;
}

async function editarLoja(botao) {
  const ids = ["nomeLoja", "telefoneLoja"];
  if (botao.textContent === "Editar") { ids.forEach(id => document.getElementById(id).disabled = false); botao.textContent = "Salvar"; return; }
  try {
    await PrazoAPI.request("/perfil/empresa", { method: "PUT", body: JSON.stringify({ nome: document.getElementById("nomeLoja").value, telefone: document.getElementById("telefoneLoja").value }) });
    ids.forEach(id => document.getElementById(id).disabled = true); botao.textContent = "Editar"; await carregarPerfil();
  } catch (erro) { alert(erro.message); }
}

async function editarUsuario(botao) {
  const ids = ["nomeUsuario", "emailUsuario", "telefoneUsuario", "cargoUsuario", "cpfUsuario"];
  if (botao.textContent === "Editar") { ids.forEach(id => document.getElementById(id).disabled = false); botao.textContent = "Salvar"; return; }
  try {
    await PrazoAPI.request("/perfil/funcionario", { method: "PUT", body: JSON.stringify({ nome_completo: document.getElementById("nomeUsuario").value, email: document.getElementById("emailUsuario").value, telefone: document.getElementById("telefoneUsuario").value, cargo: document.getElementById("cargoUsuario").value, cpf: document.getElementById("cpfUsuario").value }) });
    ids.forEach(id => document.getElementById(id).disabled = true); botao.textContent = "Editar"; await carregarPerfil();
  } catch (erro) { alert(erro.message); }
}

async function alterarSenha() {
  const nova = document.getElementById("senhaNova").value;
  if (nova !== document.getElementById("senhaConfirmar").value) return alert("As novas senhas não coincidem.");
  try { const r = await PrazoAPI.request("/perfil/senha", { method: "PUT", body: JSON.stringify({ senha_atual: document.getElementById("senhaAtual").value, senha_nova: nova }) }); alert(r.mensagem); }
  catch (erro) { alert(erro.message); }
}

async function carregarCategorias() {
  const categorias = await PrazoAPI.request("/categorias");
  document.getElementById("listaCategorias").innerHTML = categorias.map(c => '<div class="itemAcao"><div><h4>' + c.nome + '</h4><p>' + (c.descricao || 'Sem descrição') + '</p></div><div><button class="btnAcao" onclick="renomearCategoria(' + c.id_categoria + ', \'' + c.nome.replace(/'/g, "\\'") + '\')">Editar</button> <button class="btnAcao btnPerigo" onclick="excluirCategoria(' + c.id_categoria + ')">Excluir</button></div></div>').join("");
}

async function criarCategoria() {
  const nome = document.getElementById("novaCategoria").value.trim();
  const descricao = document.getElementById("descricaoCategoria").value.trim();
  const status = document.getElementById("statusCategoria");
  const botao = document.getElementById("adicionarCategoria");
  if (!nome) { status.textContent = "Informe o nome da categoria."; return; }
  botao.disabled = true;
  status.textContent = "Salvando...";
  try {
    await PrazoAPI.request("/categorias", { method: "POST", body: JSON.stringify({ nome, descricao }) });
    document.getElementById("novaCategoria").value = "";
    document.getElementById("descricaoCategoria").value = "";
    status.textContent = "Categoria adicionada com sucesso.";
    await carregarCategorias();
  } catch (erro) { status.textContent = erro.message; }
  finally { botao.disabled = false; }
}

async function renomearCategoria(id, atual) {
  const nome = prompt("Novo nome da categoria:", atual); if (!nome) return;
  try { await PrazoAPI.request("/categorias/" + id, { method: "PUT", body: JSON.stringify({ nome }) }); await carregarCategorias(); }
  catch (erro) { alert(erro.message); }
}

async function excluirCategoria(id) {
  if (!confirm("Excluir esta categoria?")) return;
  try { await PrazoAPI.request("/categorias/" + id, { method: "DELETE" }); await carregarCategorias(); }
  catch (erro) { alert(erro.message); }
}

function abrirNotificacoes() { window.location.href = "calendario.html"; }
function sairConta() { PrazoAPI.sair(); }
function trocarConta() { PrazoAPI.sair(); }
function excluirConta() { alert("Exclusão de conta não faz parte desta entrega."); }
document.getElementById("adicionarCategoria")?.addEventListener("click", criarCategoria);
carregarPerfil().catch(erro => alert(erro.message));
