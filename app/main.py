from typing import Union
import uuid

from fastapi import FastAPI, Body, Path, Query, status, HTTPException

from schemas.order_schema import InputOrder, OutputOrder
from schemas.product_schema import InputProduct, OutputProduct


app = FastAPI()


DEFAULT_QUANTITY = 100
STOCK_THRESHOLD = 10

inventory = {}
orders = {}


@app.post(
    path="/api/products/{product}",
    response_model=OutputProduct,
    status_code=status.HTTP_201_CREATED,
    tags=["Products"]
)
def create_product(product: InputProduct = Body(...)) -> OutputProduct:
    sku = str(uuid.uuid4())
    quantity = DEFAULT_QUANTITY

    inventory[sku] = {
        "sku": sku,
        "name": product.name,
        "quantity": quantity,
        "price": product.price,
    }

    return OutputProduct(**inventory[sku])


@app.patch(
    path="/api/inventories/product/{product_id}",
    response_model=OutputProduct,
    status_code=status.HTTP_200_OK,
    tags=["Products"]
)
def increment_stock(
        product_id: str = Path(...),
        quantity: Union[int, None] = Query(None)
) -> OutputProduct:
    try:
        to_add = quantity if quantity is not None else 0
        inventory[product_id]["quantity"] += to_add
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_id} not found"
        )

    return OutputProduct(**inventory[product_id])


@app.post(
    path="/api/orders",
    response_model=OutputOrder,
    status_code=status.HTTP_201_CREATED,
    tags=["Orders"]
)
def create_order(order: InputOrder = Body(...)) -> OutputOrder:
    if len(order.items) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No items send"
        )

    order_id = str(uuid.uuid4())
    reserve = {}
    products_to_buy = []
    total = 0
    detail = None

    try:
        for item in order.items:
            try:
                product = inventory[item.sku]
                if item.quantity > product["quantity"]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"No enough stock to accomplish your order"
                    )

                reserve[product["sku"]] = item.quantity
                product["quantity"] -= item.quantity

                if product["quantity"] < STOCK_THRESHOLD:
                    detail = f"ALERT: Stock for product {item.sku} is too low"
                    print(detail)

                total += (item.quantity * product["price"])

                products_to_buy.append(OutputProduct(
                    sku=product["sku"],
                    name=product["name"],
                    quantity=item.quantity,
                    price=product["price"],
                ))

            except KeyError:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product {item.sku} not found"
                )

    except HTTPException as http_e:
        return_stock(reserve)
        total = 0

        raise http_e

    orders[order_id] = OutputOrder(
        items=products_to_buy,
        total=total
    )

    return orders[order_id]


def return_stock(reserved_items: dict) -> dict:
    for sku, quantity in reserved_items.items():
        inventory[sku]["quantity"] += quantity

    return inventory