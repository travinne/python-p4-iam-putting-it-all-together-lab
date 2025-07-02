from flask import Blueprint, request, jsonify, session
from server.models import User, Recipe
from . import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    image_url = data.get('image_url', '')
    bio = data.get('bio', '')

    if not username or not password:
        return {"error": "Username and password required."}, 422

    if User.query.filter_by(username=username).first():
        return {"error": "Username already exists."}, 422

    user = User(username=username, image_url=image_url, bio=bio)
    user.password_hash = password
    db.session.add(user)
    db.session.commit()
    session['user_id'] = user.id

    return jsonify({
        "id": user.id,
        "username": user.username,
        "image_url": user.image_url,
        "bio": user.bio
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get("username")).first()

    if user and user.authenticate(data.get("password")):
        session['user_id'] = user.id
        return jsonify({
            "id": user.id,
            "username": user.username,
            "image_url": user.image_url,
            "bio": user.bio
        }), 200
    return {"error": "Unauthorized"}, 401

@auth_bp.route('/check_session', methods=['GET'])
def check_session():
    user_id = session.get('user_id')
    if not user_id:
        return {"error": "Unauthorized"}, 401

    user = db.session.get(User,user_id)
    return jsonify({
        "id": user.id,
        "username": user.username,
        "image_url": user.image_url,
        "bio": user.bio
    }), 200

@auth_bp.route('/logout', methods=['DELETE'])
def logout():
    if session.get('user_id'):
        session.pop('user_id')
        return {}, 204
    return {"error": "Unauthorized"}, 401

@auth_bp.route('/recipes', methods=['GET', 'POST'])
def recipes():
    user_id = session.get('user_id')
    if not user_id:
        return {"error": "Unauthorized"}, 401

    if request.method == 'GET':
        user = db.session.get(User,user_id)
        return jsonify([{
            "id": r.id,
            "title": r.title,
            "instructions": r.instructions,
            "minutes_to_complete": r.minutes_to_complete
        } for r in user.recipes]), 200

    if request.method == 'POST':
        data = request.get_json()
        try:
            recipe = Recipe(
                title=data.get('title'),
                instructions=data.get('instructions'),
                minutes_to_complete=data.get('minutes_to_complete'),
                user_id=user_id
            )
            db.session.add(recipe)
            db.session.commit()
            return {
                "id": recipe.id,
                "title": recipe.title,
                "instructions": recipe.instructions,
                "minutes_to_complete": recipe.minutes_to_complete
            }, 201
        except Exception as e:
            return {"error": str(e)}, 422
