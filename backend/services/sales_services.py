from decimal import Decimal

from models import Produto, Venda, VendaItem, db
from repositories import SalesRepository
from .helpers import inteiro_positivo, obrigatorios


class RegistrarSaidaProdutoService:
    def executar(self, id_loja, dados):
        obrigatorios(dados, ["id_produto", "quantidade", "tipo_saida"])
        produto = Produto.buscar_por_id(int(dados["id_produto"]))
        if not produto or produto.lote.estoque.id_loja != id_loja:
            raise LookupError("Produto não encontrado nesta loja.")
        quantidade = inteiro_positivo(dados["quantidade"], "quantidade")
        if quantidade > produto.quantidade_estoque:
            raise ValueError("Quantidade superior ao estoque disponível.")
        tipo = dados["tipo_saida"]
        if tipo not in {"vendido", "perdido"}:
            raise ValueError("tipo_saida deve ser vendido ou perdido.")
        valor_unitario = Decimal(produto.valor_unitario)
        valor_total = valor_unitario * quantidade
        venda = Venda(
            id_loja=id_loja,
            tipo_saida=tipo,
            valor_venda=valor_total,
        )
        venda.itens.append(VendaItem(produto=produto, quantidade=quantidade, valor_unitario=valor_unitario))
        produto.quantidade_estoque -= quantidade
        produto.lote.quantia_produtos = max(0, produto.lote.quantia_produtos - quantidade)
        db.session.add(venda)
        db.session.commit()
        return venda.to_dict()


class ListarSaidasService:
    def executar(self, id_loja):
        return [venda.to_dict() for venda in SalesRepository.listar_por_loja(id_loja)]
