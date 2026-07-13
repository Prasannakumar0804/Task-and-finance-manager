from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Task, User

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/tasks', methods=['POST'])
@jwt_required()
def create_task():
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()

    data = request.get_json()
    title = data.get('title')
    description = data.get('description', '')

    if not title:
        return jsonify({"error": "Title is required"}), 400

    new_task = Task(title=title, description=description, user_id=user.id)
    db.session.add(new_task)
    db.session.commit()

    return jsonify({"message": "Task created", "id": new_task.id}), 201

@tasks_bp.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()

    completed_filter = request.args.get('completed')
    query = Task.query.filter_by(user_id=user.id)

    if completed_filter is not None:
        is_completed = completed_filter.lower() == 'true'
        query = query.filter_by(completed=is_completed)

    tasks = query.all()
    result = [{
        "id": t.id,
        "title": t.title,
        "description": t.description,
        "completed": t.completed,
        "created_at": t.created_at.isoformat()
    } for t in tasks]

    return jsonify(result), 200

@tasks_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()

    task = Task.query.filter_by(id=task_id, user_id=user.id).first()
    if not task:
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json()
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.completed = data.get('completed', task.completed)

    db.session.commit()
    return jsonify({"message": "Task updated"}), 200

@tasks_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()

    task = Task.query.filter_by(id=task_id, user_id=user.id).first()
    if not task:
        return jsonify({"error": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted"}), 200