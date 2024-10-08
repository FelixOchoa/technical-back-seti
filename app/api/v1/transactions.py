from fastapi import APIRouter, Query
from app.schemas.transactions import TransactionResponse, Transaction
from app.controllers.transaction_controller import get_all_transactions_controller, create_transaction_controller, delete_transaction_controller

router = APIRouter()

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"]
)

@router.get("/get-all", response_model=list[TransactionResponse] | dict)
async def get_all_transactions(limit: int = Query(default=10, gt=0)):
    return await get_all_transactions_controller()

@router.post("/subscribe", response_model=dict)
async def subscribe_to_transactions(transaction: Transaction):
    return await create_transaction_controller(transaction)
    
@router.delete("/unsubscribe", response_model=dict)
async def unsubscribe_from_transactions(transaction_id: int):
    return await delete_transaction_controller(transaction_id)