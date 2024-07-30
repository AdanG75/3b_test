from pydantic import BaseModel, Field


class BaseProduct(BaseModel):
    name: str = Field(..., min_length=1, max_length=80)
    price: float = Field(..., ge=0)


class InputProduct(BaseProduct):
    pass


class OutputProduct(BaseProduct):
    sku: str = Field(..., min_length=31, max_length=40)
    quantity: int = Field(..., ge=0)
