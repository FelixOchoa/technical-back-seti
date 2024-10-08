from fastapi import HTTPException, Response
from app.services.transaction_services import get_all_transactions, get_index_last_transaction, create_transaction, delete_transaction, get_active_linked_funds

async def get_all_transactions_controller():
    try:
        transactions = get_all_transactions()  
        
        if not transactions:
            return { "message": "No existen transacciones" }
        
        return transactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)

async def create_transaction_controller(transaction):
    try:
        last_transaction = get_index_last_transaction()
        
        if not last_transaction:
            transaction_id = 1
        else:
            transaction_id = last_transaction['transaction_id'] + 1
            
        new_transaction = create_transaction(transaction, transaction_id)
        
        if not new_transaction:
            raise HTTPException(status_code=500, detail="No se pudo registrar la transacción")
        
        return new_transaction
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)
        
async def delete_transaction_controller(transaction_id):
    try:
        deleted_transaction = delete_transaction(transaction_id)

        return deleted_transaction
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)

async def get_active_linked_funds_controller(user_id):
    try:
        linked_funds = get_active_linked_funds(user_id)
        
        return linked_funds
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)