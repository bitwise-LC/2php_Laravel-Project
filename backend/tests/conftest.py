import os
import sys

import pytest

BACKEND = os.path.dirname(os.path.dirname(__file__))
if BACKEND not in sys.path:
    sys.path.insert(0, BACKEND)

from app import create_app
from models import db


@pytest.fixture()
def app():
    aplicacao = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "AUTO_CREATE_SCHEMA": True,
        "FRONTEND_ORIGIN": "http://127.0.0.1:5500",
    })
    yield aplicacao
    with aplicacao.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def organizacao(client):
    resposta = client.post("/api/organizacoes", json={
        "empresa": "Mercado Escola", "nome": "Ana Silva", "cpf": "111.222.333-44",
        "telefone": "(11) 99999-0000", "email": "ana@example.com", "senha": "segredo123",
        "cnpj": "12.345.678/0001-90", "endereco": "Rua Principal, 10",
    })
    assert resposta.status_code == 201
    dados = resposta.get_json()
    dados["headers"] = {
        "X-Usuario-ID": str(dados["usuario"]["id_usuario"]),
        "X-Loja-ID": str(dados["loja"]["id_loja"]),
    }
    return dados
