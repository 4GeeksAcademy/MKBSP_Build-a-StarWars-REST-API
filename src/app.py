"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""

import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Person, Planet, Favorite


app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# My See all Users or Get_All_Users
@app.route('/user', methods=['GET'])
def get_all_users():
    users = User.query.all()
    users_serialized = [user.serialize() for user in users]
    return jsonify(users_serialized), 200

# The same but for people/persons
@app.route('/people', methods=['GET'])
def get_people():
    people = Person.query.all()
    people_serialized = [person.serialize() for person in people]
    return jsonify(people_serialized), 200

# I added an add user endpoint too, I saw it in the video, and I felt it was needed.
@app.route('/user', methods=['POST'])
def create_user():
    body = request.get_json()
    # I think the IF function is working, but when I test it with Postman, I'm not getting it to reply with "You need to specify the email and password", just the 400
    if 'email' not in body or 'password' not in body:
        raise APIException("You need to specify the email and password", status_code=400)
    new_user = User(email=body['email'], password=body['password'], is_active=True)
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.serialize()), 201

# Get specific person
@app.route('/people/<int:people_id>', methods=['GET'])
def get_single_person(people_id):
    person = Person.query.get(people_id)
    if person is None:
        raise APIException("Person not found", status_code=404)
    return jsonify(person.serialize()), 200

# Get all planets
@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    planets_serialized = [planet.serialize() for planet in planets]
    return jsonify(planets_serialized), 200

# Get specific planet
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_single_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        raise APIException("Planet not found", status_code=404)
    return jsonify(planet.serialize()), 200

# I'm attempting to create a specific character or person
@app.route('/people', methods=['POST'])
def add_person():
    body = request.get_json()
    if not body:
        raise APIException("Invalid input", status_code=400)
    if 'name' not in body:
        raise APIException("You need to specify the name", status_code=400)
    new_person = Person(
        name=body['name'],
        birth_year=body.get('birth_year'),
        gender=body.get('gender'),
        height=body.get('height'),
        mass=body.get('mass'),
        hair_color=body.get('hair_color'),
        skin_color=body.get('skin_color'),
        eye_color=body.get('eye_color')
    )
    db.session.add(new_person)
    db.session.commit()
    return jsonify(new_person.serialize()), 201

# I'm attempting the update for a specific character or person
@app.route('/people/<int:people_id>', methods=['PUT'])
def update_person(people_id):
    body = request.get_json()
    if not body:
        raise APIException("Invalid input", status_code=400)
    person = Person.query.get(people_id)
    if person is None:
        raise APIException("Person not found", status_code=404)
    person.name = body.get('name', person.name)
    person.birth_year = body.get('birth_year', person.birth_year)
    person.gender = body.get('gender', person.gender)
    person.height = body.get('height', person.height)
    person.mass = body.get('mass', person.mass)
    person.hair_color = body.get('hair_color', person.hair_color)
    person.skin_color = body.get('skin_color', person.skin_color)
    person.eye_color = body.get('eye_color', person.eye_color)

    db.session.commit()
    return jsonify(person.serialize()), 200

# I'm attempting the DELETE for a specific character or person
@app.route('/people/<int:people_id>', methods=['DELETE'])
def delete_person(people_id):
    person = Person.query.get(people_id)
    if person is None:
        raise APIException("Person not found", status_code=404)
    db.session.delete(person)
    db.session.commit()
    return '', 204

# Create a new planet
@app.route('/planets', methods=['POST'])
def add_planet():
    body = request.get_json()
    if not body:
        raise APIException("Invalid input", status_code=400)
    if 'name' not in body:
        raise APIException("You need to specify the name", status_code=400)
    new_planet = Planet(
        name=body['name'],
        climate=body.get('climate'),
        terrain=body.get('terrain'),
        population=body.get('population')
    )
    db.session.add(new_planet)
    db.session.commit()
    return jsonify(new_planet.serialize()), 201

# Edit/update a specific planet
@app.route('/planets/<int:planet_id>', methods=['PUT'])
def update_planet(planet_id):
    body = request.get_json()
    if not body:
        raise APIException("Invalid input", status_code=400)
    planet = Planet.query.get(planet_id)
    if planet is None:
        raise APIException("Planet not found", status_code=404)
    
    planet.name = body.get('name', planet.name)
    planet.climate = body.get('climate', planet.climate)
    planet.terrain = body.get('terrain', planet.terrain)
    planet.population = body.get('population', planet.population)

    db.session.commit()
    return jsonify(planet.serialize()), 200

# Delete a specific planet
@app.route('/planets/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        raise APIException("Planet not found", status_code=404)
    db.session.delete(planet)
    db.session.commit()
    return '', 204

# Get all favorites for the current user
@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user_id = 1  # Replace with actual user session management
    favorites = Favorite.query.filter_by(user_id=user_id).all()
    favorites_serialized = [favorite.serialize() for favorite in favorites]
    return jsonify(favorites_serialized), 200

# Add a new favorite planet for the current user
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user_id = 1  # Replace with actual user session management
    favorite = Favorite(user_id=user_id, planet_id=planet_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify(favorite.serialize()), 201

# Add a new favorite person for the current user
@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_person(people_id):
    user_id = 1  # Replace with actual user session management
    favorite = Favorite(user_id=user_id, person_id=people_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify(favorite.serialize()), 201

# Delete a favorite planet for the current user
@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    user_id = 1  # Replace with actual user session management
    favorite = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if favorite is None:
        raise APIException("Favorite not found", status_code=404)
    db.session.delete(favorite)
    db.session.commit()
    return '', 204

# Delete a favorite person for the current user
@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_person(people_id):
    user_id = 1  # Replace with actual user session management
    favorite = Favorite.query.filter_by(user_id=user_id, person_id=people_id).first()
    if favorite is None:
        raise APIException("Favorite not found", status_code=404)
    db.session.delete(favorite)
    db.session.commit()
    return '', 204

# This only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
