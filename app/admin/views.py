from starlette.requests import Request
from starlette_admin import EnumField, PasswordField
from starlette_admin.contrib.sqla import ModelView
from starlette_admin.exceptions import FormValidationError

from app.models.category import Category
from app.models.product import Product
from app.models.user import User
from app.utils.security import get_password_hash


class AdminOnlyModelView(ModelView):
    exclude_fields_from_create = ["created_at", "updated_at"]
    exclude_fields_from_edit = ["created_at", "updated_at"]

    def is_accessible(self, request: Request) -> bool:
        user = getattr(request.state, "user", None)
        return bool(user and user.is_admin)


class CategoryAdminView(AdminOnlyModelView):
    exclude_fields_from_list = ["created_at", "updated_at"]


class ProductAdminView(AdminOnlyModelView):
    exclude_fields_from_list = ["created_at", "updated_at"]


class UserAdminView(AdminOnlyModelView):
    fields = [
        "id",
        "firstname",
        "lastname",
        "phone_number",
        EnumField("role", enum=User.Role),
        PasswordField(
            "password",
            required=False,
            help_text="Leave blank during edit to keep the current password.",
        ),
        "created_at",
        "updated_at",
    ]
    exclude_fields_from_list = ["password"]
    exclude_fields_from_detail = ["password"]
    searchable_fields = ["firstname", "lastname", "phone_number", "role"]

    async def before_create(self, request: Request, data: dict, obj: User) -> None:
        password = (data.get("password") or "").strip()
        if not password:
            raise FormValidationError({"password": "Password is required"})
        data["password"] = get_password_hash(password)

    async def before_edit(self, request: Request, data: dict, obj: User) -> None:
        password = (data.get("password") or "").strip()
        if not password:
            data.pop("password", None)
            return
        data["password"] = get_password_hash(password)


ADMIN_VIEWS = (
    (CategoryAdminView, Category, "fa fa-tags", "Categories"),
    (ProductAdminView, Product, "fa fa-box", "Products"),
    (UserAdminView, User, "fa fa-users", "Users"),
)
