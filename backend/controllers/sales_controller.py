from flask import Blueprint, jsonify

from services.sales_services import ListarSaidasService, RegistrarSaidaProdutoService
from .http import id_loja, json_body, registrar_erros


class VendaController:
    def __init__(self):
        self.blueprint = Blueprint("vendas", __name__)
        self.blueprint.add_url_rule("/api/saidas", view_func=self.listar, methods=["GET"])
        self.blueprint.add_url_rule("/api/saidas", view_func=self.registrar, methods=["POST"])
        registrar_erros(self.blueprint)

    def listar(self):
        return jsonify(ListarSaidasService().executar(id_loja())), 200

    def registrar(self):
        return jsonify(RegistrarSaidaProdutoService().executar(id_loja(), json_body())), 201


sales_blueprint = VendaController().blueprint
