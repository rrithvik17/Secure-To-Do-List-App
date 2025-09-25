import os
import time
import bcrypt
import jwt
from flask import Flask, request, jsonify
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

app = Flask(__name__)

# --- Config ---
JWT_SECRET = os.environ.get('JWT_SECRET_KEY', 'default-secret-for-dev')

# --- Database Connection ---
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
users_collection = db.users

# --- API Routes ---
@app.route('/auth/register', methods=['POST'])
def register():
    user_data = request.get_json()
    username = user_data.get('username')
    password = user_data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    if users_collection.find_one({'username': username}):
        return jsonify({"error": "Username already exists"}), 409

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    users_collection.insert_one({'username': username, 'password': hashed_password})
    
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/auth/login', methods=['POST'])
def login():
    user_data = request.get_json()
    username = user_data.get('username')
    password = user_data.get('password')

    user = users_collection.find_one({'username': username})
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        token = jwt.encode({'user_id': str(user['_id']), 'username': username}, JWT_SECRET, algorithm='HS256')
        return jsonify({'token': token})

    return jsonify({"error": "Invalid credentials"}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)