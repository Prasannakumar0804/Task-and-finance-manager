from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Transaction, User
from sqlalchemy import func, extract

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()

    transactions = Transaction.query.filter_by(user_id=user.id).all()

    total_income = sum(t.amount for t in transactions if t.type == 'income')
    total_expenses = sum(t.amount for t in transactions if t.type == 'expense')
    savings = total_income - total_expenses

    # Category-wise expense breakdown
    category_breakdown = {}
    for t in transactions:
        if t.type == 'expense':
            category_breakdown[t.category] = category_breakdown.get(t.category, 0) + t.amount

    # Monthly spending trends (expenses grouped by year-month)
    monthly_trends = {}
    for t in transactions:
        if t.type == 'expense':
            key = t.date.strftime('%Y-%m')
            monthly_trends[key] = monthly_trends.get(key, 0) + t.amount

    return jsonify({
        "total_income": total_income,
        "total_expenses": total_expenses,
        "savings": savings,
        "category_breakdown": category_breakdown,
        "monthly_trends": monthly_trends
    }), 200