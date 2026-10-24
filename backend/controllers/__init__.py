from .auth_controller import auth_blueprint
from .category_controller import category_blueprint
from .inventory_controller import inventory_blueprint
from .sales_controller import sales_blueprint

__all__ = ["auth_blueprint", "category_blueprint", "inventory_blueprint", "sales_blueprint"]
