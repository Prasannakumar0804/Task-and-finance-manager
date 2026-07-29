from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Transaction, User
from datetime import datetime

transactions_bp = Blueprint('transactions', __name__)

@transactions_bp.route('/transactions', methods=['POST'])
@jwt_required()
def create_transaction():
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()

    data = request.get_json()
    amount = data.get('amount')
    type_ = data.get('type')
    category = data.get('category')
    description = data.get('description', '')

    if amount is None or not type_ or not category:
        return jsonify({"error": "amount, type, and category are required"}), 400

    if type_ not in ['income', 'expense']:
        return jsonify({"error": "type must be 'income' or 'expense'"}), 400

    new_transaction = Transaction(
        amount=amount,
        type=type_,
        category=category,
        description=description,
        user_id=user.id
    )
    db.session.add(new_transaction)
    db.session.commit()

    return jsonify({"message": "Transaction created", "id": new_transaction.id}), 201

@transactions_bp.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()

    query = Transaction.query.filter_by(user_id=user.id)

    type_filter = request.args.get('type')
    if type_filter in ['income', 'expense']:
        query = query.filter_by(type=type_filter)

    category_filter = request.args.get('category')
    if category_filter:
        query = query.filter_by(category=category_filter)

    transactions = query.order_by(Transaction.date.desc()).all()
    result = [{
        "id": t.id,
        "amount": t.amount,
        "type": t.type,
        "category": t.category,
        "description": t.description,
        "date": t.date.isoformat()
    } for t in transactions]

    return jsonify(result), 200

@transactions_bp.route('/transactions/<int:transaction_id>', methods=['PUT'])
@jwt_required()
def update_transaction(transaction_id):
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()

    transaction = Transaction.query.filter_by(id=transaction_id, user_id=user.id).first()
    if not transaction:
        return jsonify({"error": "Transaction not found"}), 404

    data = request.get_json()
    transaction.amount = data.get('amount', transaction.amount)
    transaction.type = data.get('type', transaction.type)
    transaction.category = data.get('category', transaction.category)
    transaction.description = data.get('description', transaction.description)

    db.session.commit()
    return jsonify({"message": "Transaction updated"}), 200

@transactions_bp.route('/transactions/<int:transaction_id>', methods=['DELETE'])
@jwt_required()
def delete_transaction(transaction_id):
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()

    transaction = Transaction.query.filter_by(id=transaction_id, user_id=user.id).first()
    if not transaction:
        return jsonify({"error": "Transaction not found"}), 404

    db.session.delete(transaction)
    db.session.commit()
    return jsonify({"message": "Transaction deleted"}), 200