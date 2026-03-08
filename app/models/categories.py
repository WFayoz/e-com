from sqlalchemy import String, ForeignKey, Table, Column, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.product_category import product_category
from app.models.products import Product
from app.models.base_model import Model


class Category(Model):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    products: Mapped[list["Product"]] = relationship(
        "Product",
        secondary=product_category,
        back_populates="categories",
        lazy="selectin",
    )
