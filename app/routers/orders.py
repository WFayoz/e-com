from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from app.models.base_model import db
from app.models.cart import Cart
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.user import User
from app.schemas import ResponseSchema
from app.schemas.orders import OrderOut
from app.utils.security import get_current_user

order_router = APIRouter(prefix="/orders", tags=["orders"])


@order_router.get("")
async def get_my_orders(current_user: User = Depends(get_current_user)):
    orders = await Order.get_user_orders(current_user.id)
    return ResponseSchema[list[OrderOut]](
        message="Orders fetched",
        data=[OrderOut.model_validate(order) for order in orders],
    )


@order_router.get("/{order_id}")
async def get_order(order_id: str, current_user: User = Depends(get_current_user)):
    order = await Order.get_user_order(current_user.id, order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    return ResponseSchema[OrderOut](
        message="Order detail",
        data=OrderOut.model_validate(order),
    )


@order_router.post("/checkout")
async def checkout(current_user: User = Depends(get_current_user)):
    cart_items = await Cart.get_user_items(current_user.id)
    if not cart_items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty")

    total_amount = Decimal("0.00")
    order = Order(user_id=current_user.id, total_amount=total_amount)
    db.add(order)
    await db.flush()

    for cart_item in cart_items:
        product = await Product.get(cart_item.product_id)
        if product is None:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        if cart_item.quantity > product.availability:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for product {product.name}",
            )

        unit_price = Decimal(str(product.price))
        item_total = unit_price * cart_item.quantity
        total_amount += item_total
        product.availability -= cart_item.quantity

        db.add(
            OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=cart_item.quantity,
                unit_price=unit_price,
                total_price=item_total,
                product_name=product.name,
            )
        )
        await db.delete(cart_item)

    order.total_amount = total_amount
    await db.commit()

    saved_order = await Order.get_user_order(current_user.id, order.id)
    return ResponseSchema[OrderOut](
        message="Order created successfully",
        data=OrderOut.model_validate(saved_order),
    )
