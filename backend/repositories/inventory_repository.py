from datetime import date, timedelta

from sqlalchemy import asc, desc, func, or_, text

from models import Categoria, Estoque, Lote, Produto, db, produto_categorias


class InventoryRepository:
    @staticmethod
    def listar(id_loja, termo=None, categoria_id=None, ordem="proximo"):
        consulta = (
            Produto.query
            .join(Lote, Produto.n_lote == Lote.n_lote)
            .join(Estoque, Lote.id_estoque == Estoque.id_estoque)
            .filter(Estoque.id_loja == id_loja)
        )
        if termo:
            filtro = f"%{termo.strip()}%"
            consulta = consulta.filter(
                or_(
                    Produto.nome.ilike(filtro),
                    Produto.codigo_produto.ilike(filtro),
                    Produto.descricao.ilike(filtro),
                )
            )
        if categoria_id:
            consulta = (
                consulta.join(produto_categorias, Produto.id_produto == produto_categorias.c.id_produto)
                .filter(produto_categorias.c.id_categoria == categoria_id)
            )
        ordenacao = desc(Lote.validade) if ordem == "distante" else asc(Lote.validade)
        return consulta.order_by(ordenacao, Produto.nome.asc()).all()

    @staticmethod
    def vencimentos_no_periodo(id_loja, inicio, fim):
        return (
            Produto.query
            .join(Lote)
            .join(Estoque)
            .filter(Estoque.id_loja == id_loja, Lote.validade.between(inicio, fim))
            .order_by(Lote.validade.asc(), Produto.nome.asc())
            .all()
        )

    @staticmethod
    def proximos_do_vencimento(id_loja, dias=7):
        hoje = date.today()
        limite = hoje + timedelta(days=dias)
        # No MySQL a procedure oficial concentra a consulta especializada.
        if db.session.get_bind().dialect.name == "mysql":
            resultado = db.session.execute(
                text("CALL sp_produtos_proximos_vencimento(:id_loja, :dias)"),
                {"id_loja": id_loja, "dias": dias},
            )
            linhas = resultado.mappings().all()
            resultado.close()
            return [dict(linha) for linha in linhas]
        produtos = InventoryRepository.vencimentos_no_periodo(id_loja, hoje, limite)
        return [produto.to_dict() for produto in produtos if produto.quantidade_estoque > 0]

    @staticmethod
    def categoria_em_uso(id_categoria):
        return (
            db.session.query(func.count(produto_categorias.c.id_produto))
            .filter(produto_categorias.c.id_categoria == id_categoria)
            .scalar()
            > 0
        )
