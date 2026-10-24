from models import Categoria
from repositories import InventoryRepository
from .helpers import obrigatorios


class CadastrarCategoriaService:
    def executar(self, dados):
        obrigatorios(dados, ["nome"])
        nome = dados["nome"].strip()
        if Categoria.query.filter(Categoria.nome.ilike(nome)).first():
            raise ValueError("Categoria já cadastrada.")
        return Categoria(nome=nome, descricao=dados.get("descricao", "").strip()).salvar().to_dict()


class ListarCategoriasService:
    def executar(self):
        return [item.to_dict() for item in Categoria.query.order_by(Categoria.nome.asc()).all()]


class AtualizarCategoriaService:
    def executar(self, id_categoria, dados):
        categoria = Categoria.buscar_por_id(id_categoria)
        if not categoria:
            raise LookupError("Categoria não encontrada.")
        if dados.get("nome"):
            categoria.nome = dados["nome"].strip()
        if "descricao" in dados:
            categoria.descricao = dados["descricao"].strip()
        return categoria.atualizar().to_dict()


class ExcluirCategoriaService:
    def executar(self, id_categoria):
        categoria = Categoria.buscar_por_id(id_categoria)
        if not categoria:
            raise LookupError("Categoria não encontrada.")
        if InventoryRepository.categoria_em_uso(id_categoria):
            raise ValueError("A categoria está vinculada a produtos e não pode ser excluída.")
        categoria.deletar()
        return None
