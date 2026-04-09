import enum
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Integer, Numeric, String, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload

from app.models.base_model import Model, db

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.user import User


class Order(Model):
    class Status(enum.Enum):
        PENDING = "PENDING"
        PAID = "PAID"
        CANCELLED = "CANCELLED"

    user_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status: Mapped["Order.Status"] = mapped_column(
        Enum(Status, name="order_status"),
        default=Status.PENDING,
        nullable=False,
    )
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, nullable=False)

    user: Mapped["User"] = relationship("User")
    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
    )

    @classmethod
    async def get_user_orders(cls, user_id):
        query = (
            select(cls)
            .options(selectinload(cls.items).selectinload(OrderItem.product))
            .where(cls.user_id == user_id)
            .order_by(cls.created_at.desc())
        )
        return (await db.execute(query)).scalars().all()

    @classmethod
    async def get_user_order(cls, user_id, order_id):
        query = (
            select(cls)
            .options(selectinload(cls.items).selectinload(OrderItem.product))
            .where(cls.id == order_id, cls.user_id == user_id)
        )
        return (await db.execute(query)).scalar_one_or_none()


class OrderItem(Model):
    order_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)

    order: Mapped["Order"] = relationship("Order", back_populates="items")
    product: Mapped["Product"] = relationship("Product")
