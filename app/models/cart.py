from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload

from app.models.base_model import Model, db

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.user import User


class Cart(Model):
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    user: Mapped["User"] = relationship("User")
    product: Mapped["Product"] = relationship("Product")

    @classmethod
    async def get_user_items(cls, user_id):
        query = (
            select(cls)
            .options(selectinload(cls.product))
            .where(cls.user_id == user_id)
            .order_by(cls.created_at.desc())
        )
        return (await db.execute(query)).scalars().all()

    @classmethod
    async def get_user_product_item(cls, user_id, product_id):
        query = select(cls).where(cls.user_id == user_id, cls.product_id == product_id)
        return (await db.execute(query)).scalar_one_or_none()
