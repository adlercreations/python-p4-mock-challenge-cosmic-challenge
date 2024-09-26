#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''

@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    return jsonify([planet.to_dict() for planet in planets]), 200

@app.route('/missions', methods=['POST'])
def create_mission():
    data = request.get_json()
    try:
        # Validate data
        name = data.get('name')
        scientist_id = data.get('scientist_id')
        planet_id = data.get('planet_id')
        
        if not name or not scientist_id or not planet_id:
            raise ValueError("validation errors")

        # Create and save the mission
        new_mission = Mission(
            name=name,
            scientist_id=scientist_id,
            planet_id=planet_id
        )
        db.session.add(new_mission)
        db.session.commit()

        # Return the mission with related planet and scientist data
        return jsonify(new_mission.to_dict()), 201

    except ValueError as e:
        return jsonify({"errors": [str(e)]}), 400

@app.route('/scientists', methods=['GET', 'POST'])
def all_scientists():
    if request.method == 'GET':
        return [s.to_dict(rules=['-missions']) for s in Scientist.query.all()], 200
    elif request.method == 'POST':
        data = request.get_json()
        try:
            new_sci = Scientist(
                name=data.get('name'),
                field_of_study=data.get('field_of_study')
            )
        except ValueError:
            return {'errors': ['validation errors']}, 400
        
        db.session.add(new_sci)
        db.session.commit()
        return new_sci.to_dict(), 201

@app.route('/scientists/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def scientist_by_id(id):
    scientist = Scientist.query.filter(Scientist.id == id).first()

    if scientist is None:
        return {'error': 'Scientist not found'}, 404
    
    if request.method == 'GET':
        return scientist.to_dict(), 200
    
    elif request.method == 'PATCH':
        data = request.get_json()
        # Option A chek every field
        try:
            if 'name' in data:
                scientist.name = data['name']
            if 'field_of_study' in data:
                scientist.field_of_study = data['field_of_study']
        except ValueError:
            return {'errors': ['validation errors']}, 400

        # option B, loop through json fields and call setattr
        # for field in data:
        #     try:
        #         setattr(scientist, field, data[field])
        #     except ValueError:
        #         return {'errors': ['validation errors']}, 400

        db.session.add(scientist)
        db.session.commit()

        return scientist.to_dict(), 202
    
    elif request.method == 'DELETE':
        db.session.delete(scientist)
        db.session.commit()
        return {}, 204   

if __name__ == '__main__':
    app.run(port=5555, debug=True)
