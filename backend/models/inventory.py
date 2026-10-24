from .database import db
from .mixins import CrudMixin


produto_categorias = db.Table(
    "produto_categorias",
    db.Column("id_produto", db.Integer, db.ForeignKey("produtos.id_produto", ondelete="CASCADE"), primary_key=True),
    db.Column("id_categoria", db.Integer, db.ForeignKey("categorias.id_categoria", ondelete="CASCADE"), primary_key=True),
)


class Estoque(CrudMixin, db.Model):
    __tablename__ = "estoques"

    # Chave técnica necessária para materializar a entidade fraca do diagrama.
    id_estoque = db.Column(db.Integer, primary_key=True)
    id_loja = db.Column(db.Integer, db.ForeignKey("lojas.id_loja", ondelete="CASCADE"), nullable=False)
    nome = db.Column(db.String(80), nullable=False, default="Estoque principal")

    loja = db.relationship("Loja", back_populates="estoques")
    lotes = db.relationship("Lote", cascade="all, delete-orphan", back_populates="estoque")

    @property
    def qnt_produtos(self):
        return sum(produto.quantidade_estoque for lote in self.lotes for produto in lote.produtos)

    def to_dict(self):
        return {"id_estoque": self.id_estoque, "id_loja": self.id_loja, "nome": self.nome, "qnt_produtos": self.qnt_produtos}


class Lote(CrudMixin, db.Model):
    __tablename__ = "lotes"

    n_lote = db.Column(db.Integer, primary_key=True)
    id_estoque = db.Column(db.Integer, db.ForeignKey("estoques.id_estoque", ondelete="CASCADE"), nullable=False)
    data_fabricacao = db.Column(db.Date, nullable=False)
    validade = db.Column(db.Date, nullable=False)
    quantia_produtos = db.Column(db.Integer, nullable=False, default=0)

    estoque = db.relationship("Estoque", back_populates="lotes")
    produtos = db.relationship("Produto", cascade="all, delete-orphan", back_populates="lote")

    def to_dict(self):
        return {
            "n_lote": self.n_lote,
            "id_estoque": self.id_estoque,
            "data_fabricacao": self.data_fabricacao.isoformat(),
            "validade": self.validade.isoformat(),
            "quantia_produtos": self.quantia_produtos,
        }


class Categoria(CrudMixin, db.Model):
    __tablename__ = "categorias"

    id_categoria = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False, unique=True)
    descricao = db.Column(db.String(255), nullable=False, default="")

    produtos = db.relationship("Produto", secondary=produto_categorias, back_populates="categorias")

    def to_dict(self):
        return {"id_categoria": self.id_categoria, "nome": self.nome, "descricao": self.descricao}


class Produto(CrudMixin, db.Model):
    __tablename__ = "produtos"

    id_produto = db.Column(db.Integer, primary_key=True)
    n_lote = db.Column(db.Integer, db.ForeignKey("lotes.n_lote", ondelete="CASCADE"), nullable=False)
    codigo_produto = db.Column(db.String(60), nullable=False, unique=True)
    nome = db.Column(db.String(120), nullable=False)
    descricao = db.Column(db.String(255), nullable=False, default="")
    valor_unitario = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    quantidade_estoque = db.Column(db.Integer, nullable=False, default=0)

    lote = db.relationship("Lote", back_populates="produtos")
    categorias = db.relationship("Categoria", secondary=produto_categorias, back_populates="produtos")
    itens_venda = db.relationship("VendaItem", back_populates="produto")

    def to_dict(self):
        return {
            "id_produto": self.id_produto,
            "n_lote": self.n_lote,
            "codigo_produto": self.codigo_produto,
            "nome": self.nome,
            "descricao": self.descricao,
            "valor_unitario": float(self.valor_unitario),
            "quantidade_estoque": self.quantidade_estoque,
            "validade": self.lote.validade.isoformat() if self.lote else None,
            "data_fabricacao": self.lote.data_fabricacao.isoformat() if self.lote else None,
            "categorias": [categoria.to_dict() for categoria in self.categorias],
        }
