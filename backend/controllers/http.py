from flask import jsonify, request
from sqlalchemy.exc import DataError, IntegrityError, OperationalError, ProgrammingError, SQLAlchemyError

from models import db


def json_body():
    return request.get_json(silent=True) or {}


def id_loja():
    valor = request.headers.get("X-Loja-ID") or request.args.get("id_loja")
    if not valor:
        raise ValueError("Identificador da loja não informado.")
    return int(valor)


def id_usuario():
    valor = request.headers.get("X-Usuario-ID") or request.args.get("id_usuario")
    if not valor:
        raise ValueError("Identificador do usuário não informado.")
    return int(valor)


def registrar_erros(blueprint):
    @blueprint.errorhandler(ValueError)
    def tratar_validacao(erro):
        db.session.rollback()
        return jsonify({"erro": str(erro)}), 400

    @blueprint.errorhandler(LookupError)
    def tratar_nao_encontrado(erro):
        db.session.rollback()
        return jsonify({"erro": str(erro)}), 404

    @blueprint.errorhandler(IntegrityError)
    def tratar_integridade(_erro):
        db.session.rollback()
        return jsonify({"erro": "A operação viola uma restrição de integridade."}), 409

    @blueprint.errorhandler(DataError)
    def tratar_dado_incompativel(_erro):
        db.session.rollback()
        return jsonify({"erro": "Um dos valores informados excede o tamanho aceito pelo banco de dados."}), 400

    @blueprint.errorhandler(OperationalError)
    def tratar_conexao(_erro):
        db.session.rollback()
        return jsonify({
            "erro": "Não foi possível conectar ao MySQL. Verifique se o serviço está ativo e se DATABASE_URL contém usuário, senha, host e banco corretos."
        }), 503

    @blueprint.errorhandler(ProgrammingError)
    def tratar_schema(_erro):
        db.session.rollback()
        return jsonify({
            "erro": "O banco foi conectado, mas a estrutura esperada não foi encontrada. Execute backend/database/create_database.sql."
        }), 500

    @blueprint.errorhandler(SQLAlchemyError)
    def tratar_banco(erro):
        db.session.rollback()
        original = getattr(erro, "orig", None)
        codigo = original.args[0] if original and getattr(original, "args", None) else None
        return jsonify({
            "erro": "Falha ao acessar o banco de dados.",
            "tipo": type(erro).__name__,
            "codigo_mysql": codigo,
        }), 500
