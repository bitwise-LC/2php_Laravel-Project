let mesExibido = new Date();

async function montarCalendario() {
  PrazoAPI.exigirSessao();
  const ano = mesExibido.getFullYear(), mes = mesExibido.getMonth();
  const produtos = await PrazoAPI.request("/calendario?ano=" + ano + "&mes=" + (mes + 1));
  const porDia = produtos.reduce((mapa, p) => { const d = Number(p.validade.slice(8, 10)); (mapa[d] ||= []).push(p); return mapa; }, {});
  document.getElementById("tituloMes").textContent = mesExibido.toLocaleDateString("pt-BR", { month: "long", year: "numeric" });
  const primeiro = new Date(ano, mes, 1).getDay();
  const total = new Date(ano, mes + 1, 0).getDate();
  let html = Array.from({ length: primeiro }, () => '<div class="dia outro"></div>').join("");
  for (let dia = 1; dia <= total; dia++) {
    const itens = porDia[dia] || [];
    const hoje = new Date().toDateString() === new Date(ano, mes, dia).toDateString();
    html += '<div class="dia' + (hoje ? ' hoje' : '') + '" title="' + itens.map(p => p.nome + ' (' + p.quantidade_estoque + ')').join(', ') + '"><span>' + dia + '</span><div class="marcadores">' + itens.slice(0,5).map((_,i) => '<i class="marcador ' + ['roxo','laranja','azul','amarelo','escuro'][i] + '"></i>').join('') + '</div></div>';
  }
  document.getElementById("dias").innerHTML = html;
}

document.getElementById("anterior")?.addEventListener("click", () => { mesExibido = new Date(mesExibido.getFullYear(), mesExibido.getMonth() - 1, 1); montarCalendario(); });
document.getElementById("proximo")?.addEventListener("click", () => { mesExibido = new Date(mesExibido.getFullYear(), mesExibido.getMonth() + 1, 1); montarCalendario(); });
montarCalendario().catch(erro => alert(erro.message));
