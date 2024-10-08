from pydantic import BaseModel, Field

class Transaction(BaseModel):
    fund_id: int
    user_id: int
    amount: float = Field(gt=0, description="Monto debe ser mayor a 0")
    date: str
    uuid: str
    type: str
    transaction_id: int
    state: str
    typeNotification: str

class TransactionResponse(BaseModel):
    fund_id: int
    user_id: int
    amount: float
    date: str
    uuid: str
    type: str
    transaction_id: int
    state: str
