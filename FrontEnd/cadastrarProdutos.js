async function prepararCadastro() {
  PrazoAPI.exigirSessao();
  const categorias = await PrazoAPI.request("/categorias");
  const select = document.getElementById("categoriaProduto");
  select.innerHTML = '<option value="">Selecione uma categoria</option>' + categorias.map(c => '<option value="' + c.id_categoria + '">' + c.nome + '</option>').join("");
  document.getElementById("dataFabricacao").valueAsDate = new Date();
}

document.getElementById("formProduto")?.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  const formulario = evento.currentTarget;
  if (!formulario.reportValidity()) return;
  const botao = formulario.querySelector("button[type=submit]");
  botao.disabled = true;
  try {
    await PrazoAPI.request("/produtos", { method: "POST", body: JSON.stringify({
      nome: document.getElementById("nomeProduto").value,
      codigo_produto: document.getElementById("codigoProduto").value,
      descricao: document.getElementById("descricaoProduto").value,
      validade: document.getElementById("validadeProduto").value,
      data_fabricacao: document.getElementById("dataFabricacao").value,
      valor_unitario: document.getElementById("valorProduto").value,
      quantidade: document.getElementById("quantidadeProduto").value,
      categorias: [document.getElementById("categoriaProduto").value]
    }) });
    document.getElementById("toast").classList.add("visivel");
    setTimeout(() => { window.location.href = "estoque.html"; }, 800);
  } catch (erro) { alert(erro.message); }
  finally { botao.disabled = false; }
});

prepararCadastro().catch(erro => alert(erro.message));
