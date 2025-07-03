# server/app.py

from flask import Flask, request, session, jsonify
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError

from server.models import db, User, Recipe

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'supersecretkey'

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)
CORS(app)

# Session check before protected routes
@app.before_request
def check_if_logged_in():
    open_routes = ['signup', 'login', 'check_session']
    if request.endpoint not in open_routes and not session.get('user_id'):
        return {'error': '401 Unauthorized'}, 401

# ----------------------------
# Resource: Signup
# ----------------------------
class Signup(Resource):
    def post(self):
        data = request.get_json()

        username = data.get('username')
        password = data.get('password')
        image_url = data.get('image_url')
        bio = data.get('bio')

        try:
            new_user = User(username=username, image_url=image_url, bio=bio)
            new_user.password_hash = password  # invokes setter

            db.session.add(new_user)
            db.session.commit()

            session['user_id'] = new_user.id

            return new_user.to_dict(), 201

        except (ValueError, IntegrityError) as e:
            db.session.rollback()
            return {'errors': [str(e)]}, 422

# ----------------------------
# Resource: CheckSession
# ----------------------------
class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {}, 401

        user = db.session.get(User, user_id)
        return user.to_dict(), 200

# ----------------------------
# Resource: Login
# ----------------------------
class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()
        if user and user.authenticate(password):
            session['user_id'] = user.id
            return user.to_dict(), 200

        return {'error': '401 Unauthorized'}, 401

# ----------------------------
# Resource: Logout
# ----------------------------
class Logout(Resource):
    def delete(self):
        if not session.get('user_id'):
            return {'error': 'Unauthorized'}, 401
        session.pop('user_id')
        return {}, 204

# ----------------------------
# Resource: RecipeIndex
# ----------------------------
class RecipeIndex(Resource):
    def get(self):
        user_id = session.get('user_id')
        user = db.session.get(User, user_id)
        return [recipe.to_dict() for recipe in user.recipes], 200

    def post(self):
        data = request.get_json()

        try:
            new_recipe = Recipe(
                title=data.get('title'),
                instructions=data.get('instructions'),
                minutes_to_complete=data.get('minutes_to_complete'),
                user_id=session.get('user_id')
            )

            db.session.add(new_recipe)
            db.session.commit()

            return new_recipe.to_dict(), 201

        except (ValueError, IntegrityError) as e:
            db.session.rollback()
            return {'errors': [str(e)]}, 422

# ----------------------------
# Register Resources
# ----------------------------
api.add_resource(Signup, '/signup')
api.add_resource(CheckSession, '/check_session')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(RecipeIndex, '/recipes')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
