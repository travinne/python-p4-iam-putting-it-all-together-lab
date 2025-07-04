import pytest
from sqlalchemy.exc import IntegrityError
from server.app import app
from server.models import db, Recipe, User

class TestRecipe:
    '''Tests for the Recipe model in models.py'''

    def test_has_attributes(self):
        '''Recipe has attributes: title, instructions, and minutes_to_complete.'''
        with app.app_context():
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            user = User(username="ChefHam")
            user.password_hash = "hashedpass"
            db.session.add(user)
            db.session.commit()

            recipe = Recipe(
                title="Delicious Shed Ham",
                instructions="These are detailed cooking instructions that are long enough to pass the validation check.",
                minutes_to_complete=60,
                user_id=user.id
            )

            db.session.add(recipe)
            db.session.commit()

            new_recipe = Recipe.query.filter_by(title="Delicious Shed Ham").first()
            assert new_recipe.title == recipe.title
            assert new_recipe.instructions == recipe.instructions
            assert new_recipe.minutes_to_complete == recipe.minutes_to_complete

    def test_requires_title(self):
        '''Recipe requires each record to have a title.'''
        with app.app_context():
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            user = User(username="UserWithoutTitle")
            user.password_hash = "testpass"
            db.session.add(user)
            db.session.commit()

            recipe = Recipe(
                instructions="Valid instructions that are long enough to pass validation.",
                minutes_to_complete=30,
                user_id=user.id
            )

            with pytest.raises(IntegrityError):
                db.session.add(recipe)
                db.session.commit()

    def test_requires_50_plus_char_instructions(self):
        '''Raises error if instructions are less than 50 characters.'''
        with app.app_context():
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            user = User(username="Shorty")
            user.password_hash = "testpass"
            db.session.add(user)
            db.session.commit()

            with pytest.raises((IntegrityError, ValueError)):
                recipe = Recipe(
                    title="Short Ham",
                    instructions="Too short!",
                    minutes_to_complete=15,
                    user_id=user.id
                )
                db.session.add(recipe)
                db.session.commit()
