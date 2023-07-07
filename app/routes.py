from flask import request, jsonify, Blueprint, current_app
# from flask.globals import current_app
from werkzeug.security import generate_password_hash,check_password_hash
from flask_jwt_extended import jwt_required, get_jwt_identity, JWTManager
from .models import User, Task,Category,db
import jwt
from datetime import datetime, timedelta
import os
from app import app 
route = Blueprint('user_routes', __name__)
# /api/users/signup (POST): User sign up route
@route.route('/api/users/signup', methods=['POST'])
def signup():
    data = request.get_json()

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
            return jsonify({'error':'Please provide username, email, and password.',
            'responseCode':400}),400
    if User.query.filter_by(username=username).first():
        return jsonify({'error':'Username already esist',
            'responseCode':409}),409
    if User.query.filter_by(email=email).first():
        return jsonify({'error':'email already exist',
            'responseCode':409}),409
    hashed_pssword = generate_password_hash(password) 
    new_user = User(username = username, email= email, password= hashed_pssword) 
    db.session.add(new_user)
    db.session.commit()     
    return jsonify({'message':'User created successfully.', 'responseCode':200}),200      

# /api/users/login (POST): User login route
@route.route('/api/users/login', methods=['POST'])
def login():
    # Retrieve the username and password from the request body
    username = request.json.get('username')
    password = request.json.get('password')
    if not username or not password:
        return jsonify({'error': 'Username and password are required.'}), 400
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        token = generate_token(user)
        return jsonify({'token': token}), 200
    else:
        return jsonify({'error': 'Invalid username or password.'}), 401

def generate_token(user):
    # secret_key = 'TRDXFGDFCXDGVGSGCFDFDCF'
    secret_key = current_app.config['JWT_SECRET_KEY']
    expiration = datetime.utcnow() + timedelta(days=1)
    payload = {
        'sub': user.id,  # Set the subject claim with the user ID or appropriate identifier
        'user_id': user.id,
        'username': user.username,
        'email': user.email
    }

    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token
# /api/users/logout (POST): User logout route
# /api/tasks (GET): Get all user's tasks
@route.route('/api/tasks', methods=['GET'])
@jwt_required()
def get_user_tasks():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    tasks = Task.query.filter_by(user=user).all()

    response = []
    for task in tasks:
        response.append({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'due_date': task.due_date.isoformat(),
            'created_at': task.created_at.isoformat(),
            'updated_at': task.updated_at.isoformat(),
            'status': task.status,
            'user_id': task.user_id
        })

    return jsonify(response), 200
 
# /api/tasks (POST): Create a new task
@route.route('/api/tasks', methods=['POST'])
@jwt_required() 
def create_task():
    current_user_id = get_jwt_identity() 
    user = User.query.get(current_user_id) 
    
    title = request.json.get('title')
    description = request.json.get('description')
    status = request.json.get('status')
    due_date = request.json.get('due_date')
    if not title:
        return jsonify({'error': 'Task title is required.', 'responseCode':400}), 400
    new_task = Task(title=title, description=description, status=status, due_date=due_date, user=user)
    db.session.add(new_task)
    db.session.commit()
    return jsonify({'message': 'Task created successfully.','responseCode':200, 'task_id': new_task.id}), 201

# /api/tasks/<task_id> (GET): Get details of a specific task
@route.route('/api/tasks/<int:task_id>', methods=['GET','PUT','DELETE'])
@jwt_required()
def get_update_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found.'}), 404

    if request.method == 'GET':
        task_data = {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'user_id': task.user_id,
            'due_date': task.due_date,
            'created_at': task.created_at
        }
        return jsonify(task_data), 200

    elif request.method == 'PUT':
        title = request.json.get('title')
        description = request.json.get('description')
        status = request.json.get('status')
        if not title:
            return jsonify({'error': 'Task title is required.'}), 400
        task.title = title
        task.description = description
        task.status = status
        db.session.commit()
        return jsonify({'message': 'Task updated successfully.', 'task_id': task.id}), 200

    elif request.method == 'DELETE':
            db.session.delete(task)
            db.session.commit()

            return jsonify({'message': 'Task deleted successfully.'}), 200

@route.route('/api/tasks/<int:task_id>/complete', methods=['PATCH'])
@jwt_required()  # Requires a valid JWT token in the request headers
def mark_task_as_complete(task_id):
    current_user_id = get_jwt_identity()  # Retrieve the current user's ID from the JWT token
    user = User.query.get(current_user_id)  # Get the user object based on the ID

    task = Task.query.filter_by(id=task_id, user_id=user.id).first()  # Retrieve the task based on the task ID and user ID

    if not task:
        return jsonify({'error': 'Task not found.'}), 404

    # Mark the task as complete
    task.status = 'Complete'
    db.session.commit()

    return jsonify({'message': 'Task marked as complete.'}), 200    
@route.route('/api/tasks/<int:task_id>/incomplete', methods=['PATCH'])
@jwt_required()  # Requires a valid JWT token in the request headers
def mark_task_as_incomplete(task_id):
    current_user_id = get_jwt_identity()  # Retrieve the current user's ID from the JWT token
    user = User.query.get(current_user_id)  # Get the user object based on the ID

    task = Task.query.filter_by(id=task_id, user_id=user.id).first()  # Retrieve the task based on the task ID and user ID

    if not task:
        return jsonify({'error': 'Task not found.'}), 404

    # Mark the task as complete
    task.status = 'Incomplete'
    db.session.commit()

    return jsonify({'message': 'Task marked as incomplete.'}), 200   
# /api/tasks/<task_id>/assign (POST): Assign a task to another user
@route.route('/api/tasks/<int:task_id>/assign', methods=['POST'])
@jwt_required()  
def assign_task(task_id):
    current_user_id = get_jwt_identity()  
    user = User.query.get(current_user_id) 
    task = Task.query.filter_by(id=task_id, user_id=user.id).first()

    if not task:
        return jsonify({'error': 'Task not found.'}), 404

    assignee_id = request.json.get('assignee_id')
    if not assignee_id:
        return jsonify({'error': 'Assignee ID is required.'}), 400

    assignee = User.query.get(assignee_id)

    if not assignee:
        return jsonify({'error': 'Assignee not found.'}), 404

    task.user_id = assignee_id
    db.session.commit()

    return jsonify({'message': 'Task assigned successfully.'}), 200
# /api/categories (GET): Get all categories
@route.route('/api/categories', methods=['GET'])
@jwt_required()  
def get_categories():
    categories = Category.query.all()

    category_names = []
    for category in categories:
        category_names.append(category.name)
    return jsonify(category_names), 200
# /api/categories (POST): Create a new category
@route.route('/api/categories', methods=['POST'])
def create_category():
    category_name = request.json.get('name')
    if not category_name:
        return jsonify({'error': 'Category name is required.'}), 400
    existing_category = Category.query.filter_by(name=category_name).first()
    if existing_category:
        return jsonify({'error': 'Category with the same name already exists.'}), 409
    new_category = Category(name=category_name)
    db.session.add(new_category)
    db.session.commit()
    return jsonify({'message': 'Category created successfully.', 'category_id': new_category.id}), 201