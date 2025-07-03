from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.exc import IntegrityError
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)

    recipes = db.relationship('Recipe', backref='user', cascade='all, delete-orphan')

    serialize_rules = ('-recipes.user', '-_password_hash',)

    def __repr__(self):
        return f"<User {self.username}>"

    @hybrid_property
    def password_hash(self):
        raise AttributeError("Password hashes may not be viewed.")

    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = bcrypt.generate_password_hash(password.encode('utf-8')).decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))

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


class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'

    __table_args__ = (
        db.CheckConstraint('length(instructions) >= 50', name='instructions_length_check'),
    )

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    serialize_rules = ('-user.recipes',)

    def __repr__(self):
        return f"<Recipe {self.id}: {self.title}>"

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


# Optional helper functions for testing or debugging

def create_user(username, password, image_url=None, bio=None):
    user = User(username=username, image_url=image_url, bio=bio)
    user.password_hash = password
    try:
        db.session.add(user)
        db.session.commit()
        return user
    except IntegrityError as e:
        db.session.rollback()
        print(f"Error creating user: {e}")
        return None


def create_recipe(title, instructions, minutes_to_complete, user_id):
    recipe = Recipe(
        title=title,
        instructions=instructions,
        minutes_to_complete=minutes_to_complete,
        user_id=user_id
    )
    try:
        db.session.add(recipe)
        db.session.commit()
        return recipe
    except IntegrityError as e:
        db.session.rollback()
        print(f"Error creating recipe: {e}")
        return None
