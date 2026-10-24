let produtosSaida = [];

async function prepararSaida() {
  PrazoAPI.exigirSessao();
  produtosSaida = (await PrazoAPI.request("/produtos")).filter(p => p.quantidade_estoque > 0);
  const select = document.getElementById("produtoSaida");
  select.innerHTML = '<option value="">Selecione um produto</option>' + produtosSaida.map(p => '<option value="' + p.id_produto + '">' + p.nome + ' (' + p.quantidade_estoque + ' un.)</option>').join("");
  select.addEventListener("change", () => {
    const produto = produtosSaida.find(p => p.id_produto === Number(select.value));
    document.getElementById("infoProduto").textContent = produto ? 'Validade: ' + PrazoAPI.dataBR(produto.validade) + ' · ' + PrazoAPI.moeda(produto.valor_unitario) + ' por unidade' : '';
    if (produto) document.getElementById("quantidadeSaida").max = produto.quantidade_estoque;
  });
}

document.getElementById("formSaida")?.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  const tipo = document.querySelector('input[name="validade"]:checked');
  if (!tipo || !evento.currentTarget.reportValidity()) return;
  try {
    await PrazoAPI.request("/saidas", { method: "POST", body: JSON.stringify({
      id_produto: document.getElementById("produtoSaida").value,
      quantidade: document.getElementById("quantidadeSaida").value,
      tipo_saida: tipo.value === "salvo" ? "vendido" : "perdido"
    }) });
    document.getElementById("toast").classList.add("visivel");
    setTimeout(() => { window.location.href = "dashboard.html"; }, 800);
  } catch (erro) { alert(erro.message); }
});

prepararSaida().catch(erro => alert(erro.message));
