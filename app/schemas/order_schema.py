from pydantic import BaseModel, Field

from app.schemas.product_schema import OutputProduct


class BaseItem(BaseModel):
    sku: str = Field(..., min_length=31, max_length=40)
    quantity: int = Field(..., ge=0)


class InputOrder(BaseModel):
    items: list[BaseItem] = Field(...)


class OutputOrder(BaseModel):
    items: list[OutputProduct]
    total: float = Field(..., ge=0)
    detail: str = Field(None)
