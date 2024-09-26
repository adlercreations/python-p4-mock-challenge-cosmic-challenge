from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


class Planet(db.Model, SerializerMixin):
    __tablename__ = 'planets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    distance_from_earth = db.Column(db.Integer)
    nearest_star = db.Column(db.String)

    # Add relationship
    missions = db.relationship('Mission', back_populates='planet')
    # Add serialization rules
    serialize_rules = ('-missions',)

    def __repr__(self) -> str:
        return f'<Scientist {self.name} {self.distance_from_earth} {self.nearest_star}>'

class Scientist(db.Model, SerializerMixin):
    __tablename__ = 'scientists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    field_of_study = db.Column(db.String, nullable = False)

    # Add relationship
    missions = db.relationship(
        'Mission', 
        back_populates='scientist',
        cascade="all, delete-orphan"
    )
    # Add serialization rules
    serialize_rules = ('-missions.scientist', '-missions.planet')
    # Add validation
    @validates('name', 'field_of_study')
    def validate_not_null(self, key, new_value):
        if not new_value:
            raise ValueError(f'{key} cannot be empty')
        else:
            return new_value

    def __repr__(self) -> str:
        return f'<Scientist {self.name} {self.field_of_study}>'


class Mission(db.Model, SerializerMixin):
    __tablename__ = 'missions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    scientist_id = db.Column(db.Integer, db.ForeignKey('scientists.id'), nullable = False)
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'), nullable = False)

    # Add relationships
    scientist = db.relationship('Scientist', back_populates='missions')
    planet = db.relationship('Planet', back_populates='missions')
    # Add serialization rules
    serialize_rules = ('-scientist.missions', '-planet.missions')
    # Add validation
    @validates('scientist_id', 'planet_id')
    def validate_not_null(self, key, new_value):
        if new_value is None:
            raise ValueError(f'{key} cannot be empty')
        else:
            return new_value
        
    @validates('name')
    def validate_not_empty_string(self, key, new_value):
        if new_value is None or len(new_value) == 0:
            raise ValueError(f'{key} cannot be empty')
        else:
            return new_value

    def __repr__(self) -> str:
        return f'<Mission {self.name} {self.scientist_id} {self.planet_id}>'

# add any models you may need.
