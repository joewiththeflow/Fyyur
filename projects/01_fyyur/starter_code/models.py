from email.policy import default
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

venue_genres = db.Table('venue_genres',
  db.Column('venue_id', db.Integer, db.ForeignKey('venue.id', ondelete='CASCADE'), primary_key=True),
  db.Column('genre_id', db.Integer, db.ForeignKey('genre.id', ondelete='CASCADE'),primary_key=True)
)

artist_genres = db.Table('artist_genres',
  db.Column('artist_id', db.Integer, db.ForeignKey('artist.id', ondelete='CASCADE'), primary_key=True),
  db.Column('genre_id', db.Integer, db.ForeignKey('genre.id', ondelete='CASCADE'), primary_key=True)
)

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    genres = db.relationship('Genre', secondary=venue_genres, cascade='all,delete', backref=db.backref('venues', lazy=True))
    city = db.Column(db.String(80), nullable=False)
    state = db.Column(db.String(2), nullable=False)
    address = db.Column(db.String(120), nullable=False, unique=True)
    phone = db.Column(db.String(15), nullable=True, unique=True)
    image_link = db.Column(db.String(500), nullable=True, unique=True)
    facebook_link = db.Column(db.String(120), nullable=True, unique=True)
    website = db.Column(db.String(120), nullable=True, unique=True)
    seeking_talent = db.Column(db.Boolean, nullable=False, default=True)
    seeking_description = db.Column(db.String(500), nullable=True)
    shows = db.relationship('Show', cascade='all,delete', backref=db.backref('venue'))

    def __repr__(self):
      return f'<Venue ID: {self.id}, Name: {self.name}, Genres: {self.genres}, City: {self.city}, State: {self.state}, Address: {self.address}, Phone: {self.phone}, Image Link: {self.image_link}, Facebook Link: {self.facebook_link}, Website: {self.website}, Seeking Talent?: {self.seeking_talent}, Seeking Description: {self.seeking_description}>'
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    genres = db.relationship('Genre', secondary=artist_genres, cascade='all,delete', backref=db.backref('artists', lazy=True))
    city = db.Column(db.String(80), nullable=False)
    state = db.Column(db.String(2), nullable=False)
    phone = db.Column(db.String(15), nullable=True, unique=True)
    image_link = db.Column(db.String(500), nullable=True, unique=True)
    facebook_link = db.Column(db.String(120), nullable=True, unique=True)
    website = db.Column(db.String(120), nullable=True, unique=True)
    seeking_venue = db.Column(db.Boolean, nullable=False, default=True)
    seeking_description = db.Column(db.String(500), nullable=True)

    def __repr__(self):
      return f'<Artist ID: {self.id}, Name: {self.name}, Genres: {self.genres}, City: {self.city}, State: {self.state}, Phone: {self.phone}, Image Link: {self.image_link}, Facebook Link: {self.facebook_link}, Website: {self.website}, Seeking Venue?: {self.seeking_venue}, Seeking Description: {self.seeking_description}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Genre(db.Model):
    __tablename__ = 'genre'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)

    def __repr__(self):
      return f'<Genre ID: {self.id}, Name: {self.name}>'

class Show(db.Model):
  __tablename__ = 'shows'
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id', ondelete='CASCADE'), primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id', ondelete='CASCADE'), primary_key=True)
  start_time = db.Column(db.DateTime, primary_key=True)
  artist = db.relationship('Artist', backref=db.backref('shows', cascade='all,delete'))

  def __init__(self, venue, artist, start_time):
    self.venue_id = venue.id
    self.artist_id = artist.id
    self.start_time = start_time