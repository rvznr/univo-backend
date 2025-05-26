from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models import User, Feedback  

bcrypt = Bcrypt()

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    required_fields = ['school_id', 'name', 'surname', 'email', 'password', 'gender']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email is already registered"}), 409

    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')

    user = User(
        school_id=data['school_id'],
        name=data['name'],
        surname=data['surname'],
        email=data['email'],
        password=hashed_password,
        gender=data['gender']
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Registration successful"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Invalid email or password"}), 401

    access_token = create_access_token(identity=str(user.id))
    return jsonify({
        "message": "Login successful",
        "access_token": access_token,  
        "user_id": user.id
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))

    if not user:
        return jsonify({'msg': 'User not found!'}), 404

    return jsonify({
        'name': user.name,
        'email': user.email,
        'schoolId': user.school_id,
        'gender': user.gender
    })
