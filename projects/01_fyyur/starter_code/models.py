from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import datetime

app     = Flask(__name__)
app.config.from_object('config')
db      = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String, unique=True, nullable=False)
    city          = db.Column(db.String(120), nullable=False)
    state         = db.Column(db.String(120), nullable=False)
    address       = db.Column(db.String(120), nullable=False)
    phone         = db.Column(db.String(120), nullable=False)
    image_link    = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120), nullable=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres              = db.Column(db.ARRAY(db.String), nullable=False)
    website             = db.Column(db.String, nullable=True)
    seeking_talent      = db.Column(db.Boolean, default=True, nullable=False)
    seeking_description = db.Column(db.String, default='We are on the lookout for a local artist to play every two weeks. Please call us.', nullable=False)
    shows               = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
        return f'<Venue ID: {self.id}, Name: {self.name}, State: {self.state}, City: {self.city}>'

class Artist(db.Model):
    __tablename__ = 'artists'

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String, unique=True, nullable=False)
    city          = db.Column(db.String(120), nullable=False)
    state         = db.Column(db.String(120), nullable=False)
    phone         = db.Column(db.String(120), nullable=False)
    genres        = db.Column(db.ARRAY(db.String), nullable=False)
    image_link    = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120), nullable=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website             = db.Column(db.String, nullable=True)
    seeking_venue       = db.Column(db.Boolean, default=True, nullable=False)
    seeking_description = db.Column(db.String, default='Looking for shows to perform at in awesome venues.', nullable=False)
    shows               = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
        return f'<Artist ID: {self.id}, Name: {self.name}, State: {self.state}, City: {self.city}>'

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'shows'

    id         = db.Column(db.Integer, primary_key=True)
    time_start = db.Column(db.DateTime, default=datetime.datetime.now(), nullable=False)
    venue_id   = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    artist_id  = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)

    def __repr__(self):
        return f'<Show ID: {self.id}| start: {self.time_start}>| Venue ID: {self.venue_id}| Artist ID: {self.artist_id}'
