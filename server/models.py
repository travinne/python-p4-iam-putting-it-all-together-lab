from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)

    recipes = db.relationship("Recipe", backref="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username}>"

    # password_hash property
    @property
    def password_hash(self):
        raise AttributeError("Password hashes may not be viewed.")

    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = generate_password_hash(password)

    def authenticate(self, password):
        return check_password_hash(self._password_hash, password)

    @validates("username")
    def validate_username(self, key, value):
        if not value or value.strip() == "":
            raise ValueError("Username is required.")
        return value

    @validates("_password_hash")
    def validate_password_hash(self, key, value):
        if not value or value.strip() == "":
            raise ValueError("Password hash is required.")
        return value


class Recipe(db.Model):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __repr__(self):
        return f"<Recipe {self.title}>"

    @validates("title")
    def validate_title(self, key, value):
        if not value or value.strip() == "":
            raise ValueError("Title is required.")
        return value

    @validates("instructions")
    def validate_instructions(self, key, value):
        if not value or len(value.strip()) < 50:
            raise ValueError("Instructions must be at least 50 characters.")
        return value
