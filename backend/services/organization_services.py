from werkzeug.security import check_password_hash, generate_password_hash

from models import (
    Empresa, EmpresaTelefone, Estoque, Funcionario, FuncionarioTelefone,
    Loja, Usuario, db,
)
from repositories import ProfileRepository
from .helpers import obrigatorios


class CadastrarOrganizacaoService:
    def executar(self, dados):
        obrigatorios(dados, ["empresa", "nome", "cpf", "telefone", "email", "senha"])
        if Funcionario.query.filter_by(email=dados["email"].strip().lower()).first():
            raise ValueError("E-mail já cadastrado.")
        if Funcionario.query.filter_by(cpf=dados["cpf"].strip()).first():
            raise ValueError("CPF já cadastrado.")
        cpf_numerico = "".join(caractere for caractere in dados["cpf"] if caractere.isdigit())
        cnpj_provisorio = f"PEND-{cpf_numerico}"[:18]
        empresa = Empresa(
            nome=dados["empresa"].strip(),
            cnpj=dados.get("cnpj", cnpj_provisorio).strip(),
            endereco_sede=dados.get("endereco", "Endereço não informado").strip(),
        )
        empresa.telefones.append(EmpresaTelefone(telefone=dados["telefone"].strip()))
        loja = Loja(endereco=empresa.endereco_sede, n_funcionarios=1)
        empresa.lojas.append(loja)
        loja.estoques.append(Estoque(nome="Estoque principal"))
        funcionario = Funcionario(
            cpf=dados["cpf"].strip(),
            nome_completo=dados["nome"].strip(),
            email=dados["email"].strip().lower(),
            cargo=dados.get("cargo", "Responsável").strip(),
            endereco=empresa.endereco_sede,
        )
        funcionario.telefones.append(FuncionarioTelefone(telefone=dados["telefone"].strip()))
        funcionario.usuario = Usuario(senha=generate_password_hash(dados["senha"]))
        loja.funcionarios.append(funcionario)
        db.session.add(empresa)
        db.session.commit()
        return {"usuario": funcionario.usuario.to_dict(), "funcionario": funcionario.to_dict(), "loja": loja.to_dict(), "empresa": empresa.to_dict()}


class AutenticarUsuarioService:
    def executar(self, dados):
        obrigatorios(dados, ["email", "senha"])
        funcionario = Funcionario.query.filter_by(email=dados["email"].strip().lower()).first()
        if not funcionario or not funcionario.usuario or not check_password_hash(funcionario.usuario.senha, dados["senha"]):
            raise ValueError("E-mail ou senha inválidos.")
        return {"id_usuario": funcionario.usuario.id_usuario, "id_loja": funcionario.id_loja, "nome": funcionario.nome_completo}


class ConsultarPerfilService:
    def executar(self, id_usuario):
        usuario = ProfileRepository.buscar_por_usuario(id_usuario)
        if not usuario:
            raise LookupError("Usuário não encontrado.")
        funcionario = usuario.funcionario
        loja = funcionario.loja
        return {"usuario": usuario.to_dict(), "funcionario": funcionario.to_dict(), "loja": loja.to_dict(), "empresa": loja.empresa.to_dict()}


class AtualizarEmpresaLojaService:
    def executar(self, id_usuario, dados):
        usuario = ProfileRepository.buscar_por_usuario(id_usuario)
        if not usuario:
            raise LookupError("Usuário não encontrado.")
        empresa, loja = usuario.funcionario.loja.empresa, usuario.funcionario.loja
        empresa.nome = dados.get("nome", empresa.nome).strip()
        empresa.cnpj = dados.get("cnpj", empresa.cnpj).strip()
        empresa.endereco_sede = dados.get("endereco_sede", empresa.endereco_sede).strip()
        loja.endereco = dados.get("endereco", loja.endereco).strip()
        if dados.get("telefone"):
            if empresa.telefones:
                empresa.telefones[0].telefone = dados["telefone"].strip()
            else:
                empresa.telefones.append(EmpresaTelefone(telefone=dados["telefone"].strip()))
        db.session.commit()
        return {"empresa": empresa.to_dict(), "loja": loja.to_dict()}


class AtualizarFuncionarioService:
    def executar(self, id_usuario, dados):
        usuario = ProfileRepository.buscar_por_usuario(id_usuario)
        if not usuario:
            raise LookupError("Usuário não encontrado.")
        funcionario = usuario.funcionario
        for campo in ["nome_completo", "email", "cpf", "cargo", "endereco"]:
            if dados.get(campo):
                setattr(funcionario, campo, dados[campo].strip())
        if dados.get("telefone"):
            if funcionario.telefones:
                funcionario.telefones[0].telefone = dados["telefone"].strip()
            else:
                funcionario.telefones.append(FuncionarioTelefone(telefone=dados["telefone"].strip()))
        db.session.commit()
        return funcionario.to_dict()


class AlterarSenhaService:
    def executar(self, id_usuario, dados):
        obrigatorios(dados, ["senha_atual", "senha_nova"])
        usuario = Usuario.buscar_por_id(id_usuario)
        if not usuario:
            raise LookupError("Usuário não encontrado.")
        if not check_password_hash(usuario.senha, dados["senha_atual"]):
            raise ValueError("Senha atual incorreta.")
        if len(dados["senha_nova"]) < 6:
            raise ValueError("A nova senha deve ter ao menos 6 caracteres.")
        usuario.senha = generate_password_hash(dados["senha_nova"])
        usuario.atualizar()
        return {"mensagem": "Senha alterada com sucesso."}
