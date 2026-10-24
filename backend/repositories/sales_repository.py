from models import Venda


class SalesRepository:
    @staticmethod
    def listar_por_loja(id_loja, limite=50):
        return (
            Venda.query
            .filter_by(id_loja=id_loja)
            .order_by(Venda.data_venda.desc())
            .limit(limite)
            .all()
        )
