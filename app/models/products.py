from sqlalchemy import Integer, String, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship


from app.models.base_model import Model
from app.models.product_category import product_category


class Product(Model):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    discount_percentage: Mapped[float] = mapped_column(Numeric(5, 2), default=0, nullable=False)

    rating: Mapped[float] = mapped_column(Numeric(3, 2), default=0, nullable=False)
    availability: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    categories: Mapped[list["Category"]] = relationship(
        "Category",
        secondary=product_category,
        back_populates="products",
        lazy="selectin",
    )

    @property
    def discounted_price(self) -> float:
        # Numeric -> Decimal, so cast to float safely
        price = float(self.price)
        discount = float(self.discount_percentage)
        return round(price * (1 - discount / 100), 2)
