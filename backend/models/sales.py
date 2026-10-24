from datetime import datetime, timezone

from .database import db
from .mixins import CrudMixin


class Venda(CrudMixin, db.Model):
    __tablename__ = "vendas"

    id_venda = db.Column(db.Integer, primary_key=True)
    id_loja = db.Column(db.Integer, db.ForeignKey("lojas.id_loja"), nullable=False)
    data_venda = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    valor_venda = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    tipo_saida = db.Column(db.String(20), nullable=False, default="vendido")

    loja = db.relationship("Loja", back_populates="vendas")
    itens = db.relationship("VendaItem", cascade="all, delete-orphan", back_populates="venda")

    @property
    def qnt_itens(self):
        return sum(item.quantidade for item in self.itens)

    def to_dict(self):
        return {
            "id_venda": self.id_venda,
            "id_loja": self.id_loja,
            "data_venda": self.data_venda.isoformat(),
            "valor_venda": float(self.valor_venda),
            "tipo_saida": self.tipo_saida,
            "qnt_itens": self.qnt_itens,
            "itens": [item.to_dict() for item in self.itens],
        }


class VendaItem(CrudMixin, db.Model):
    __tablename__ = "venda_itens"

    id_item = db.Column(db.Integer, primary_key=True)
    id_venda = db.Column(db.Integer, db.ForeignKey("vendas.id_venda", ondelete="CASCADE"), nullable=False)
    id_produto = db.Column(db.Integer, db.ForeignKey("produtos.id_produto"), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    valor_unitario = db.Column(db.Numeric(10, 2), nullable=False, default=0)

    venda = db.relationship("Venda", back_populates="itens")
    produto = db.relationship("Produto", back_populates="itens_venda")

    def to_dict(self):
        return {
            "id_item": self.id_item,
            "id_produto": self.id_produto,
            "produto": self.produto.nome if self.produto else None,
            "quantidade": self.quantidade,
            "valor_unitario": float(self.valor_unitario),
        }
