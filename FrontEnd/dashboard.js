async function carregarDashboard() {
  PrazoAPI.exigirSessao();
  try {
    const resumo = await PrazoAPI.request("/dashboard");
    document.getElementById("valorSalvo").textContent = PrazoAPI.moeda(resumo.valor_salvo);
    document.getElementById("quantidadeSalvos").textContent = resumo.produtos_salvos;
    document.getElementById("valorPerdido").textContent = PrazoAPI.moeda(resumo.valor_perdido);
    document.getElementById("quantidadePerdidos").textContent = resumo.produtos_perdidos;
    document.getElementById("proximosVencimento").textContent = resumo.proximos_vencimento;
    document.getElementById("totalProdutos").textContent = resumo.total_produtos;
  } catch (erro) { alert(erro.message); }
}

carregarDashboard();
