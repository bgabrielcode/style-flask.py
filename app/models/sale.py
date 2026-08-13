from pydantic import BaseModel
from datetime import date

class sale(BaseModel):
    sale_date: date
    product_id: str
    quantity: int
    total_valor: float