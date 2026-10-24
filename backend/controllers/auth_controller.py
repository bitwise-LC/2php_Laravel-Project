from flask import Blueprint, jsonify

from services.organization_services import (
    AlterarSenhaService, AtualizarEmpresaLojaService, AtualizarFuncionarioService,
    AutenticarUsuarioService, CadastrarOrganizacaoService, ConsultarPerfilService,
)
from .http import id_usuario, json_body, registrar_erros


class AuthController:
    def __init__(self):
        self.blueprint = Blueprint("auth", __name__)
        self._registrar_rotas()
        registrar_erros(self.blueprint)

    def _registrar_rotas(self):
        self.blueprint.add_url_rule("/api/organizacoes", view_func=self.cadastrar, methods=["POST"])
        self.blueprint.add_url_rule("/api/auth/login", view_func=self.login, methods=["POST"])
        self.blueprint.add_url_rule("/api/perfil", view_func=self.consultar_perfil, methods=["GET"])
        self.blueprint.add_url_rule("/api/perfil/empresa", view_func=self.atualizar_empresa, methods=["PUT"])
        self.blueprint.add_url_rule("/api/perfil/funcionario", view_func=self.atualizar_funcionario, methods=["PUT"])
        self.blueprint.add_url_rule("/api/perfil/senha", view_func=self.alterar_senha, methods=["PUT"])

    def cadastrar(self):
        return jsonify(CadastrarOrganizacaoService().executar(json_body())), 201

    def login(self):
        return jsonify(AutenticarUsuarioService().executar(json_body())), 200

    def consultar_perfil(self):
        return jsonify(ConsultarPerfilService().executar(id_usuario())), 200

    def atualizar_empresa(self):
        return jsonify(AtualizarEmpresaLojaService().executar(id_usuario(), json_body())), 200

    def atualizar_funcionario(self):
        return jsonify(AtualizarFuncionarioService().executar(id_usuario(), json_body())), 200

    def alterar_senha(self):
        return jsonify(AlterarSenhaService().executar(id_usuario(), json_body())), 200


auth_blueprint = AuthController().blueprint
