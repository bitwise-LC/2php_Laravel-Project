from calendar import monthrange
from datetime import date
from decimal import Decimal, InvalidOperation

from models import Categoria, Estoque, Lote, Produto, db
from repositories import AnalyticsRepository, InventoryRepository
from .helpers import data_iso, inteiro_positivo, obrigatorios


class RegistrarEntradaProdutoService:
    def executar(self, id_loja, dados):
        obrigatorios(dados, ["nome", "codigo_produto", "validade", "data_fabricacao", "valor_unitario", "quantidade"])
        if Produto.query.filter_by(codigo_produto=dados["codigo_produto"].strip()).first():
            raise ValueError("Código de produto já cadastrado.")
        quantidade = inteiro_positivo(dados["quantidade"], "quantidade")
        fabricacao = data_iso(dados["data_fabricacao"], "data_fabricacao")
        validade = data_iso(dados["validade"], "validade")
        if validade < fabricacao:
            raise ValueError("A validade não pode ser anterior à fabricação.")
        try:
            valor = Decimal(str(dados["valor_unitario"]))
        except InvalidOperation as erro:
            raise ValueError("valor_unitario inválido.") from erro
        if valor < 0:
            raise ValueError("valor_unitario não pode ser negativo.")
        estoque = Estoque.query.filter_by(id_loja=id_loja).order_by(Estoque.id_estoque.asc()).first()
        if not estoque:
            estoque = Estoque(id_loja=id_loja, nome="Estoque principal")
            db.session.add(estoque)
        lote = Lote(
            estoque=estoque,
            data_fabricacao=fabricacao,
            validade=validade,
            quantia_produtos=quantidade,
        )
        produto = Produto(
            lote=lote,
            codigo_produto=dados["codigo_produto"].strip(),
            nome=dados["nome"].strip(),
            descricao=dados.get("descricao", "").strip(),
            valor_unitario=valor,
            quantidade_estoque=quantidade,
        )
        # Adiciona o agregado à sessão antes das consultas de categoria para
        # que o autoflush preserve corretamente Estoque -> Lote -> Produto.
        db.session.add(produto)
        ids_categorias = dados.get("categorias", [])
        if dados.get("id_categoria"):
            ids_categorias.append(dados["id_categoria"])
        for identificador in {int(item) for item in ids_categorias if item}:
            categoria = Categoria.buscar_por_id(identificador)
            if not categoria:
                raise ValueError(f"Categoria {identificador} não encontrada.")
            produto.categorias.append(categoria)
        db.session.commit()
        return produto.to_dict()


class ListarEstoqueService:
    def executar(self, id_loja):
        return [item.to_dict() for item in InventoryRepository.listar(id_loja)]


class PesquisarProdutoService:
    def executar(self, id_loja, termo):
        if not termo or not termo.strip():
            raise ValueError("Informe um termo para pesquisa.")
        return [item.to_dict() for item in InventoryRepository.listar(id_loja, termo=termo)]


class FiltrarOrdenarEstoqueService:
    def executar(self, id_loja, categoria_id=None, ordem="proximo"):
        if ordem not in {"proximo", "distante"}:
            raise ValueError("Ordenação inválida.")
        return [item.to_dict() for item in InventoryRepository.listar(id_loja, categoria_id=categoria_id, ordem=ordem)]


class AtualizarProdutoService:
    def executar(self, id_produto, dados):
        produto = Produto.buscar_por_id(id_produto)
        if not produto:
            raise LookupError("Produto não encontrado.")
        for campo in ["nome", "codigo_produto", "descricao"]:
            if dados.get(campo):
                setattr(produto, campo, dados[campo].strip())
        if dados.get("valor_unitario") is not None:
            produto.valor_unitario = Decimal(str(dados["valor_unitario"]))
        if dados.get("quantidade") is not None:
            quantidade = inteiro_positivo(dados["quantidade"], "quantidade")
            produto.quantidade_estoque = quantidade
            produto.lote.quantia_produtos = quantidade
        if dados.get("validade"):
            produto.lote.validade = data_iso(dados["validade"], "validade")
        if dados.get("data_fabricacao"):
            produto.lote.data_fabricacao = data_iso(dados["data_fabricacao"], "data_fabricacao")
        if produto.lote.validade < produto.lote.data_fabricacao:
            raise ValueError("A validade não pode ser anterior à fabricação.")
        if "categorias" in dados:
            produto.categorias = []
            for identificador in {int(item) for item in dados["categorias"] if item}:
                categoria = Categoria.buscar_por_id(identificador)
                if not categoria:
                    raise ValueError(f"Categoria {identificador} não encontrada.")
                produto.categorias.append(categoria)
        db.session.commit()
        return produto.to_dict()


class ExcluirProdutoService:
    def executar(self, id_produto):
        produto = Produto.buscar_por_id(id_produto)
        if not produto:
            raise LookupError("Produto não encontrado.")
        if produto.itens_venda:
            raise ValueError("Produto com histórico de saída não pode ser excluído.")
        lote = produto.lote
        produto.deletar()
        if lote and not lote.produtos:
            lote.deletar()
        return None


class ConsultarCalendarioVencimentosService:
    def executar(self, id_loja, ano, mes):
        try:
            ano, mes = int(ano), int(mes)
            ultimo_dia = monthrange(ano, mes)[1]
        except (TypeError, ValueError) as erro:
            raise ValueError("Ano ou mês inválido.") from erro
        produtos = InventoryRepository.vencimentos_no_periodo(id_loja, date(ano, mes, 1), date(ano, mes, ultimo_dia))
        return [produto.to_dict() for produto in produtos]


class ListarAlertasVencimentoService:
    def executar(self, id_loja, dias=7):
        dias = inteiro_positivo(dias, "dias")
        if dias > 365:
            raise ValueError("O período máximo é de 365 dias.")
        return InventoryRepository.proximos_do_vencimento(id_loja, dias)


class ConsultarResumoEstoqueService:
    def executar(self, id_loja):
        return AnalyticsRepository.resumo_estoque(id_loja)


class GerarPacotesPromocionaisService:
    def executar(self, id_loja):
        produtos = InventoryRepository.proximos_do_vencimento(id_loja, 14)
        pacotes = []
        for indice in range(0, len(produtos), 2):
            itens = produtos[indice:indice + 2]
            if not itens:
                continue
            menor_validade = min(item["validade"] for item in itens)
            pacotes.append({
                "id": indice // 2 + 1,
                "nome": " + ".join(item["nome"] for item in itens),
                "produtos": itens,
                "desconto_sugerido": 20,
                "validade_mais_proxima": menor_validade,
            })
        return pacotes
