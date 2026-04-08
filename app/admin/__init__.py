from fastapi import FastAPI
from starlette_admin.contrib.sqla import Admin

from app.admin.auth import AdminAuthProvider
from app.admin.views import ADMIN_VIEWS
from app.models.base_model import db


def setup_admin(app: FastAPI) -> None:
    admin = Admin(
        db.engine,
        title="E-Com Admin",
        base_url="/admin",
        auth_provider=AdminAuthProvider(),
    )

    for view_class, model, icon, label in ADMIN_VIEWS:
        admin.add_view(view_class(model, icon=icon, label=label))

    admin.mount_to(app)
