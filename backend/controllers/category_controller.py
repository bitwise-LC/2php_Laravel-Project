from flask import Blueprint, jsonify

from services.category_services import (
    AtualizarCategoriaService, CadastrarCategoriaService,
    ExcluirCategoriaService, ListarCategoriasService,
)
from .http import json_body, registrar_erros


class CategoriaController:
    def __init__(self):
        self.blueprint = Blueprint("categorias", __name__)
        self.blueprint.add_url_rule("/api/categorias", view_func=self.listar, methods=["GET"])
        self.blueprint.add_url_rule("/api/categorias", view_func=self.cadastrar, methods=["POST"])
        self.blueprint.add_url_rule("/api/categorias/<int:id_categoria>", view_func=self.atualizar, methods=["PUT"])
        self.blueprint.add_url_rule("/api/categorias/<int:id_categoria>", view_func=self.excluir, methods=["DELETE"])
        registrar_erros(self.blueprint)

    def listar(self):
        return jsonify(ListarCategoriasService().executar()), 200

    def cadastrar(self):
        return jsonify(CadastrarCategoriaService().executar(json_body())), 201

    def atualizar(self, id_categoria):
        return jsonify(AtualizarCategoriaService().executar(id_categoria, json_body())), 200

    def excluir(self, id_categoria):
        ExcluirCategoriaService().executar(id_categoria)
        return "", 204


category_blueprint = CategoriaController().blueprint
