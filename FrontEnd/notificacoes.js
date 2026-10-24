async function carregarPromocoes() {
  PrazoAPI.exigirSessao();
  try {
    const pacotes = await PrazoAPI.request("/promocoes/sugestoes");
    document.getElementById("listaPacotes").innerHTML = pacotes.length ? pacotes.map(p => '<article class="pacote"><h2>' + p.nome + '</h2><p>Vencimento mais próximo: ' + PrazoAPI.dataBR(p.validade_mais_proxima) + '</p><strong>' + p.desconto_sugerido + '% de desconto sugerido</strong></article>').join('') : '<p>Não há produtos próximos do vencimento para montar pacotes.</p>';
  } catch (erro) { alert(erro.message); }
}
carregarPromocoes();
