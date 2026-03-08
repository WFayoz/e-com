from sqlalchemy import Table, Column, ForeignKey

from app.models.base_model import Base


product_category = Table(
    "product_category",
    Base.metadata,
    Column("product_id", ForeignKey("products.id", ondelete="CASCADE"), primary_key=True),
    Column("category_id", ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True),
)