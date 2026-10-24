from datetime import date, datetime, time, timedelta

from sqlalchemy import case, func

from models import Estoque, Lote, Produto, Venda, VendaItem, db


class AnalyticsRepository:
    @staticmethod
    def resumo_estoque(id_loja):
        hoje = date.today()
        limite = hoje + timedelta(days=7)
        linha = (
            db.session.query(
                func.coalesce(func.sum(Produto.quantidade_estoque), 0).label("total"),
                func.coalesce(func.sum(case((Lote.validade < hoje, Produto.quantidade_estoque), else_=0)), 0).label("vencidos"),
                func.coalesce(func.sum(case((Lote.validade.between(hoje, limite), Produto.quantidade_estoque), else_=0)), 0).label("proximos"),
            )
            .join(Lote, Produto.n_lote == Lote.n_lote)
            .join(Estoque, Lote.id_estoque == Estoque.id_estoque)
            .filter(Estoque.id_loja == id_loja)
            .one()
        )
        inicio_mes = datetime.combine(hoje.replace(day=1), time.min)
        vendas = (
            db.session.query(
                Venda.tipo_saida,
                func.coalesce(func.sum(Venda.valor_venda), 0),
                func.coalesce(func.sum(VendaItem.quantidade), 0),
            )
            .join(VendaItem, Venda.id_venda == VendaItem.id_venda)
            .filter(Venda.id_loja == id_loja, Venda.data_venda >= inicio_mes)
            .group_by(Venda.tipo_saida)
            .all()
        )
        saidas = {tipo: {"valor": float(valor), "quantidade": int(qtd)} for tipo, valor, qtd in vendas}
        return {
            "total_produtos": int(linha.total),
            "proximos_vencimento": int(linha.proximos),
            "vencidos": int(linha.vencidos),
            "valor_salvo": saidas.get("vendido", {}).get("valor", 0),
            "produtos_salvos": saidas.get("vendido", {}).get("quantidade", 0),
            "valor_perdido": saidas.get("perdido", {}).get("valor", 0),
            "produtos_perdidos": saidas.get("perdido", {}).get("quantidade", 0),
        }
