from models import Empresa, Funcionario, Loja, Usuario


class ProfileRepository:
    @staticmethod
    def buscar_por_usuario(id_usuario):
        return (
            Usuario.query
            .join(Funcionario, Usuario.n_funcionario == Funcionario.n_funcionario)
            .join(Loja, Funcionario.id_loja == Loja.id_loja)
            .join(Empresa, Loja.id_empresa == Empresa.id_empresa)
            .filter(Usuario.id_usuario == id_usuario)
            .first()
        )
