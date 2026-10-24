let estoqueAtual = [];

function cardProduto(produto) {
  const categorias = produto.categorias.map(c => c.nome).join(", ") || "Sem categoria";
  return '<article class="produto"><div class="produto-nome" title="' + produto.descricao + '">' + produto.nome + '</div>' +
    '<small>' + produto.quantidade_estoque + ' un. · ' + PrazoAPI.dataBR(produto.validade) + '<br>' + categorias + '</small>' +
    '<div class="acoes"><button class="alterar" onclick="editarProduto(' + produto.id_produto + ')">Alterar</button>' +
    '<button class="excluir" onclick="excluirProduto(' + produto.id_produto + ')">Excluir</button></div></article>';
}

async function carregarEstoque() {
  PrazoAPI.exigirSessao();
  const termo = document.getElementById("busca").value.trim();
  const ordem = document.getElementById("filtro").value;
  estoqueAtual = await PrazoAPI.request("/produtos?ordem=" + encodeURIComponent(ordem) + (termo ? "&q=" + encodeURIComponent(termo) : ""));
  document.getElementById("lista").innerHTML = estoqueAtual.length ? estoqueAtual.map(cardProduto).join("") : "<p>Nenhum produto encontrado.</p>";
}

function editarProduto(id) {
  const produto = estoqueAtual.find(p => p.id_produto === id);
  document.getElementById("editarId").value = id;
  document.getElementById("editarNome").value = produto.nome;
  document.getElementById("editarQuantidade").value = produto.quantidade_estoque;
  document.getElementById("editarValidade").value = produto.validade;
  document.getElementById("janelaEdicao").classList.add("aberta");
}

async function excluirProduto(id) {
  if (!confirm("Excluir este produto do estoque?")) return;
  try { await PrazoAPI.request("/produtos/" + id, { method: "DELETE" }); await carregarEstoque(); }
  catch (erro) { alert(erro.message); }
}

document.getElementById("formEdicao")?.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  try {
    await PrazoAPI.request("/produtos/" + document.getElementById("editarId").value, { method: "PUT", body: JSON.stringify({
      nome: document.getElementById("editarNome").value,
      quantidade: document.getElementById("editarQuantidade").value,
      validade: document.getElementById("editarValidade").value
    }) });
    document.getElementById("janelaEdicao").classList.remove("aberta");
    await carregarEstoque();
  } catch (erro) { alert(erro.message); }
});

document.getElementById("cancelarEdicao")?.addEventListener("click", () => document.getElementById("janelaEdicao").classList.remove("aberta"));
document.getElementById("busca")?.addEventListener("input", () => { clearTimeout(window.buscaPrazo); window.buscaPrazo = setTimeout(carregarEstoque, 250); });
document.getElementById("filtro")?.addEventListener("change", carregarEstoque);
carregarEstoque().catch(erro => alert(erro.message));
