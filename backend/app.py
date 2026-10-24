import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify
from sqlalchemy.exc import OperationalError, ProgrammingError, SQLAlchemyError
from flask_cors import CORS

# Config avalia os.getenv no momento em que é importada. O arquivo precisa
# ser carregado antes dessa importação para evitar a URL padrão root:senha.
ENV_PATH = Path(__file__).resolve().with_name(".env")
load_dotenv(ENV_PATH, override=True)

from config import Config
from controllers import auth_blueprint, category_blueprint, inventory_blueprint, sales_blueprint
from models import db


def create_app(configuracao=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if configuracao:
        app.config.update(configuracao)

    db.init_app(app)
    origens_frontend = {
        app.config["FRONTEND_ORIGIN"],
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    }
    CORS(app, origins=list(origens_frontend), supports_credentials=False)

    for blueprint in [auth_blueprint, category_blueprint, inventory_blueprint, sales_blueprint]:
        app.register_blueprint(blueprint)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "aplicacao": "Prazo Certo"})

    @app.get("/api/health/database")
    def health_database():
        try:
            db.session.execute(db.text("SELECT 1"))
            return jsonify({"status": "ok", "banco": "conectado"})
        except OperationalError as erro:
            db.session.rollback()
            codigo = erro.orig.args[0] if getattr(erro, "orig", None) and erro.orig.args else None
            causas = {
                1045: "Usuário ou senha recusados pelo MySQL.",
                1049: "O banco prazo_certo não existe.",
                2003: "O servidor MySQL não está acessível no host e porta configurados.",
            }
            return jsonify({
                "status": "erro",
                "banco": "indisponível",
                "codigo_mysql": codigo,
                "causa": causas.get(codigo, "Falha operacional ao conectar ao MySQL."),
            }), 503
        except ProgrammingError:
            db.session.rollback()
            return jsonify({
                "status": "erro",
                "banco": "estrutura_incompleta",
                "causa": "O MySQL respondeu, mas as tabelas esperadas não foram encontradas.",
            }), 500
        except SQLAlchemyError:
            db.session.rollback()
            return jsonify({
                "status": "erro",
                "banco": "indisponível",
                "orientacao": "Confira DATABASE_URL e execute database/create_database.sql."
            }), 503

    # Exclusivo para testes automatizados; a execução normal usa create_database.sql.
    if app.config.get("AUTO_CREATE_SCHEMA"):
        with app.app_context():
            db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true",
    )
