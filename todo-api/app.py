import os
import time
import jwt
from flask import Flask, request, jsonify
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from bson.objectid import ObjectId
from functools import wraps

app = Flask(__name__)

# --- Config ---
JWT_SECRET = os.environ.get('JWT_SECRET_KEY', 'default-secret-for-dev')

# --- Database Connection ---
# (Keep your existing get_mongo_client function here)
def get_mongo_client():
    db_user = os.environ.get('MONGO_USER')
    db_password = os.environ.get('MONGO_PASSWORD')
    db_host = os.environ.get('MONGO_HOST', 'todo-db-service')
    mongo_uri = f"mongodb://{db_user}:{db_password}@{db_host}:27017/?authSource=admin"
    for i in range(5):
        try:
            client = MongoClient(mongo_uri, serverSelectionTimeoutMS=3000)
            client.admin.command('ping')
            return client
        except ConnectionFailure:
            time.sleep(3)
    return None

client = get_mongo_client()
if not client:
    exit(1)
db = client.tododb
tasks_collection = db.tasks

# --- Token Decorator ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            current_user = {'user_id': data['user_id'], 'username': data['username']}
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# --- API Routes ---
@app.route('/api/tasks', methods=['GET'])
@token_required
def get_tasks(current_user):
    tasks = []
    for task in tasks_collection.find({'user_id': current_user['user_id']}):
        task['_id'] = str(task['_id'])
        tasks.append(task)
    return jsonify(tasks)

@app.route('/api/tasks', methods=['POST'])
@token_required
def add_task(current_user):
    task_data = request.get_json()
    new_task = {
        'description': task_data['description'],
        'completed': False,
        'user_id': current_user['user_id']
    }
    result = tasks_collection.insert_one(new_task)
    created_task = tasks_collection.find_one({'_id': result.inserted_id})
    created_task['_id'] = str(created_task['_id'])
    return jsonify(created_task), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)