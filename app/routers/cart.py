from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from app.models.base_model import db
from app.models.cart import Cart
from app.models.product import Product
from app.models.user import User
from app.schemas import ResponseSchema
from app.schemas.cart import AddToCart, CartItemOut, UpdateCartItem
from app.utils.security import get_current_user

cart_router = APIRouter(prefix="/cart", tags=["cart"])


@cart_router.get("")
async def get_cart(current_user: User = Depends(get_current_user)):
    items = await Cart.get_user_items(current_user.id)
    return ResponseSchema[list[CartItemOut]](
        message="Cart fetched",
        data=[CartItemOut.model_validate(item) for item in items],
    )


@cart_router.post("")
async def add_to_cart(data: AddToCart, current_user: User = Depends(get_current_user)):
    product = await Product.get(data.product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    existing_item = await Cart.get_user_product_item(current_user.id, data.product_id)
    new_quantity = data.quantity if existing_item is None else existing_item.quantity + data.quantity
    if new_quantity > product.availability:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Requested quantity exceeds available stock",
        )

    if existing_item is None:
        item = Cart(user_id=current_user.id, product_id=data.product_id, quantity=data.quantity)
        db.add(item)
    else:
        existing_item.quantity = new_quantity
        item = existing_item

    await db.commit()
    await db.refresh(item)
    item = (await Cart.get_user_items(current_user.id))
    saved_item = next(cart_item for cart_item in item if cart_item.product_id == data.product_id)
    return ResponseSchema[CartItemOut](
        message="Item added to cart",
        data=CartItemOut.model_validate(saved_item),
    )


@cart_router.patch("/{item_id}")
async def update_cart_item(
    item_id: str,
    data: UpdateCartItem,
    current_user: User = Depends(get_current_user),
):
    item = await Cart.get(item_id)
    if item is None or item.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")

    product = await Product.get(item.product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    if data.quantity > product.availability:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Requested quantity exceeds available stock",
        )

    item.quantity = data.quantity
    await db.commit()
    refreshed = (await Cart.get_user_items(current_user.id))
    saved_item = next(cart_item for cart_item in refreshed if str(cart_item.id) == item_id)
    return ResponseSchema[CartItemOut](
        message="Cart item updated",
        data=CartItemOut.model_validate(saved_item),
    )


@cart_router.delete("/{item_id}")
async def del_cart_item(item_id: str, current_user: User = Depends(get_current_user)):
    item = await Cart.get(item_id)
    if item is None or item.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")

    await Cart.delete(item_id)
    return ResponseSchema(message="Cart item deleted")
