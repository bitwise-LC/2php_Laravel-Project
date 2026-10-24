from datetime import date

from flask import Blueprint, jsonify, request

from services.inventory_services import (
    AtualizarProdutoService, ConsultarCalendarioVencimentosService,
    ConsultarResumoEstoqueService, ExcluirProdutoService,
    FiltrarOrdenarEstoqueService, GerarPacotesPromocionaisService,
    ListarAlertasVencimentoService, ListarEstoqueService,
    PesquisarProdutoService, RegistrarEntradaProdutoService,
)
from .http import id_loja, json_body, registrar_erros


class EstoqueController:
    def __init__(self):
        self.blueprint = Blueprint("estoque", __name__)
        self.blueprint.add_url_rule("/api/produtos", view_func=self.listar, methods=["GET"])
        self.blueprint.add_url_rule("/api/produtos", view_func=self.cadastrar, methods=["POST"])
        self.blueprint.add_url_rule("/api/produtos/<int:id_produto>", view_func=self.atualizar, methods=["PUT"])
        self.blueprint.add_url_rule("/api/produtos/<int:id_produto>", view_func=self.excluir, methods=["DELETE"])
        self.blueprint.add_url_rule("/api/calendario", view_func=self.calendario, methods=["GET"])
        self.blueprint.add_url_rule("/api/alertas", view_func=self.alertas, methods=["GET"])
        self.blueprint.add_url_rule("/api/dashboard", view_func=self.dashboard, methods=["GET"])
        self.blueprint.add_url_rule("/api/promocoes/sugestoes", view_func=self.promocoes, methods=["GET"])
        registrar_erros(self.blueprint)

    def listar(self):
        loja = id_loja()
        termo = request.args.get("q")
        categoria = request.args.get("categoria")
        ordem = request.args.get("ordem")
        if termo:
            dados = PesquisarProdutoService().executar(loja, termo)
        elif categoria or ordem:
            dados = FiltrarOrdenarEstoqueService().executar(loja, categoria, ordem or "proximo")
        else:
            dados = ListarEstoqueService().executar(loja)
        return jsonify(dados), 200

    def cadastrar(self):
        return jsonify(RegistrarEntradaProdutoService().executar(id_loja(), json_body())), 201

    def atualizar(self, id_produto):
        return jsonify(AtualizarProdutoService().executar(id_produto, json_body())), 200

    def excluir(self, id_produto):
        ExcluirProdutoService().executar(id_produto)
        return "", 204

    def calendario(self):
        hoje = date.today()
        ano = request.args.get("ano", hoje.year)
        mes = request.args.get("mes", hoje.month)
        return jsonify(ConsultarCalendarioVencimentosService().executar(id_loja(), ano, mes)), 200

    def alertas(self):
        return jsonify(ListarAlertasVencimentoService().executar(id_loja(), request.args.get("dias", 7))), 200

    def dashboard(self):
        return jsonify(ConsultarResumoEstoqueService().executar(id_loja())), 200

    def promocoes(self):
        return jsonify(GerarPacotesPromocionaisService().executar(id_loja())), 200


inventory_blueprint = EstoqueController().blueprint
