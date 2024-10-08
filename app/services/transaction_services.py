from app.core.config import db_fs, firestore
import uuid
import datetime

def get_all_transactions():
    try:
        list_transactions = []
        
        transactions = db_fs.collection("transaction").stream()
            
        for transaction in transactions:
            list_transactions.append(transaction.to_dict())
        
        _temp = get_info_funds_by_id_fund(list_transactions)
        print(_temp) 
        return _temp 
    except Exception as e:
        print(e)
        
def get_index_last_transaction():
    try:
        last_transaction = db_fs.collection("transaction").order_by('transaction_id', direction=firestore.Query.DESCENDING).limit(1).stream()
        
        for transaction in last_transaction:
            return transaction.to_dict()
    
    except Exception as e:
        print(e)
        
def create_transaction(transaction, transaction_id):
    try:
        user = get_user_info(transaction.user_id)
        
        if user['balance'] < transaction.amount:
            return {"message": "Saldo insuficiente.", "type": 1, "error": True}
        
        for funds in user['linked_funds']:
            if funds == transaction.fund_id:
                return {"message": "Ya has invertido en este fondo.", "type": 2, "error": True}
        
        fund = get_fund_info(transaction.fund_id)
        
        if fund["minimal_link_amount"] > transaction.amount:
            return {"message": "No tiene saldo disponible para vincularse al fondo: " + fund["name"], "type": 3, "error": True}
                
        new_transaction = {
            "fund_id": transaction.fund_id,
            "user_id": transaction.user_id,
            "amount": transaction.amount,
            "date": transaction.date,
            "uuid": str(uuid.uuid4()),
            "type": transaction.type,
            "transaction_id": transaction_id,
            "state": transaction.state
        }
                
        db_fs.collection("transaction").add(new_transaction)
        send_notification(new_transaction, transaction.typeNotification, db_fs, 'Completada', 'Se suscribió correctamente al fondo.')
        _temp = db_fs.collection("users").where('id', '==', transaction.user_id).stream()
        
        for document in _temp:
            db_fs.collection("users").document(document.id).update({'balance': firestore.Increment(-transaction.amount)})
            db_fs.collection("users").document(document.id).update({'linked_funds': firestore.ArrayUnion([transaction.fund_id])})
            db_fs.collection("users").document(document.id).update({'transactions': firestore.ArrayUnion([transaction_id])})

        return { "message": "Transacción registrada correctamente.", "transaction_id": transaction_id, "error": False }
    except Exception as e:
        print(e)
        
def delete_transaction(transaction_id):
    try:
        exist_document = db_fs.collection('transaction').where('transaction_id', '==', transaction_id).stream()
        
        _temp_transaction = {}
        _document_id = ""
                        
        for document in exist_document:
            _temp_transaction = document.to_dict()
            _document_id = document.id
            
        if _document_id == "":
            return {"message": "La transacción no existe.", "type": 1, "error": True}
            
        if _temp_transaction['state'] == "Cancelada":
            return {"message": "La transacción ya fue cancelada.", "type": 2, "error": True}
        
        if _temp_transaction:
            _temp_user_ref = db_fs.collection('users').where('id', '==', _temp_transaction['user_id']).stream()
            db_fs.collection('transaction').document(_document_id).update({'state': "Cancelada"})
            
            last_transaction = get_index_last_transaction()
            
            for document in _temp_user_ref:
                db_fs.collection('users').document(document.id).update({'linked_funds': firestore.ArrayRemove([_temp_transaction['fund_id']])})
                db_fs.collection('users').document(document.id).update({'balance' : firestore.Increment(_temp_transaction['amount'])})
                db_fs.collection("users").document(document.id).update({'transactions': firestore.ArrayUnion([last_transaction['transaction_id'] + 1])})          
            
            new_transaction = {
            "fund_id": _temp_transaction['fund_id'],
            "user_id": _temp_transaction['user_id'],
            "amount": -_temp_transaction['amount'],
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "uuid": str(uuid.uuid4()),
            "type": "Cancelación",
            "transaction_id": last_transaction['transaction_id'] + 1,
            "state": "Cancelada"
            }
            
            db_fs.collection("transaction").add(new_transaction)
            send_notification(new_transaction, 'email', db_fs, 'Cancelada', 'Se canceló correctamente la suscripción al fondo.')


        return {"message": "Transacción cancelada correctamente.", "transaction_id": transaction_id, "error": False}
    except Exception as e:
        print(e)
        
def get_user_info(user_id):
    try:
        user = db_fs.collection('users').where('id', '==', user_id).stream()
        
        for document in user:
            return document.to_dict()
    except Exception as e:
        print(e)
        
def get_fund_info(fund_id):
    try:
        fund = db_fs.collection('funds').where('id', '==', fund_id).stream()
        
        for document in fund:
            return document.to_dict()
    except Exception as e:
        print(e)
        
def send_notification(transaction, typeNotification, db_fs, state, message):
    try:
        last_notification = db_fs.collection("notifications").order_by('id', direction=firestore.Query.DESCENDING).limit(1).stream()
        _temp_notification = {}
        
        for notification in last_notification:
            _temp_notification = notification.to_dict()
         
        new_notification = {
            'id': _temp_notification['id'] + 1,
            'fund_id': transaction['fund_id'],
            'user_id': transaction['user_id'],
            'state': state,
            'message': message,
            'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'type': typeNotification,
            'transaction_id': transaction['transaction_id']
        }
        
        db_fs.collection("notifications").add(new_notification)
        return True
        
    except Exception as e:
        print(e)
       
def get_active_linked_funds(user_id):
    try:
        user = db_fs.collection('users').where('id', '==', user_id).stream()
        _temp_linked_funds = []
        
        for document in user:
            _temp_linked_funds = document.to_dict()['linked_funds']
        
        get_funds = db_fs.collection('funds').where('id', 'in', _temp_linked_funds).stream()
        _temp = []
        
        for document in get_funds:
            _temp.append(document.to_dict())
                    
        return {"message": "Fondos vinculados.", "linked_funds": _temp, "error": False}
    except Exception as e:
        print(e)
        
def get_info_funds_by_id_fund(funds):
    try:
        _list_funds_id = []
        for transaction in funds:
            _list_funds_id.append(transaction['fund_id'])
            
        get_funds = db_fs.collection('funds').where('id', 'in', _list_funds_id).stream()
        _temp = []
        
        for document in get_funds:
            _temp.append(document.to_dict())
        
        for transaction in funds:
            for fund in _temp:
                if fund['id'] == transaction['fund_id']:
                    transaction['fund_info'] = fund  
        return funds
    except Exception as e:
        print(e)