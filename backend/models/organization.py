from datetime import datetime, timezone

from .database import db
from .mixins import CrudMixin


class Empresa(CrudMixin, db.Model):
    __tablename__ = "empresas"

    id_empresa = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    cnpj = db.Column(db.String(18), nullable=False, unique=True)
    endereco_sede = db.Column(db.String(255), nullable=False)

    telefones = db.relationship("EmpresaTelefone", cascade="all, delete-orphan", back_populates="empresa")
    lojas = db.relationship("Loja", cascade="all, delete-orphan", back_populates="empresa")

    def to_dict(self):
        return {
            "id_empresa": self.id_empresa,
            "nome": self.nome,
            "cnpj": self.cnpj,
            "endereco_sede": self.endereco_sede,
            "telefones": [item.telefone for item in self.telefones],
        }


class EmpresaTelefone(CrudMixin, db.Model):
    __tablename__ = "empresa_telefones"

    id_telefone = db.Column(db.Integer, primary_key=True)
    id_empresa = db.Column(db.Integer, db.ForeignKey("empresas.id_empresa", ondelete="CASCADE"), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    empresa = db.relationship("Empresa", back_populates="telefones")


class Loja(CrudMixin, db.Model):
    __tablename__ = "lojas"

    id_loja = db.Column(db.Integer, primary_key=True)
    id_empresa = db.Column(db.Integer, db.ForeignKey("empresas.id_empresa"), nullable=False)
    n_funcionarios = db.Column(db.Integer, nullable=False, default=0)
    endereco = db.Column(db.String(255), nullable=False)

    empresa = db.relationship("Empresa", back_populates="lojas")
    funcionarios = db.relationship("Funcionario", back_populates="loja")
    estoques = db.relationship("Estoque", cascade="all, delete-orphan", back_populates="loja")
    vendas = db.relationship("Venda", back_populates="loja")

    def to_dict(self):
        return {
            "id_loja": self.id_loja,
            "id_empresa": self.id_empresa,
            "n_funcionarios": self.n_funcionarios,
            "endereco": self.endereco,
        }


class Funcionario(CrudMixin, db.Model):
    __tablename__ = "funcionarios"

    n_funcionario = db.Column(db.Integer, primary_key=True)
    id_loja = db.Column(db.Integer, db.ForeignKey("lojas.id_loja"), nullable=False)
    cpf = db.Column(db.String(14), nullable=False, unique=True)
    nome_completo = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    cargo = db.Column(db.String(80), nullable=False, default="Responsável")
    endereco = db.Column(db.String(255), nullable=False)

    loja = db.relationship("Loja", back_populates="funcionarios")
    telefones = db.relationship("FuncionarioTelefone", cascade="all, delete-orphan", back_populates="funcionario")
    usuario = db.relationship("Usuario", uselist=False, cascade="all, delete-orphan", back_populates="funcionario")

    def to_dict(self):
        return {
            "n_funcionario": self.n_funcionario,
            "id_loja": self.id_loja,
            "cpf": self.cpf,
            "nome_completo": self.nome_completo,
            "email": self.email,
            "cargo": self.cargo,
            "endereco": self.endereco,
            "telefones": [item.telefone for item in self.telefones],
        }


class FuncionarioTelefone(CrudMixin, db.Model):
    __tablename__ = "funcionario_telefones"

    id_telefone = db.Column(db.Integer, primary_key=True)
    n_funcionario = db.Column(db.Integer, db.ForeignKey("funcionarios.n_funcionario", ondelete="CASCADE"), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    funcionario = db.relationship("Funcionario", back_populates="telefones")


class Usuario(CrudMixin, db.Model):
    __tablename__ = "usuarios"

    id_usuario = db.Column(db.Integer, primary_key=True)
    n_funcionario = db.Column(db.Integer, db.ForeignKey("funcionarios.n_funcionario", ondelete="CASCADE"), nullable=False, unique=True)
    senha = db.Column(db.String(255), nullable=False)
    data_cadastro = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    funcionario = db.relationship("Funcionario", back_populates="usuario")

    def to_dict(self):
        return {
            "id_usuario": self.id_usuario,
            "n_funcionario": self.n_funcionario,
            "data_cadastro": self.data_cadastro.isoformat() if self.data_cadastro else None,
        }
