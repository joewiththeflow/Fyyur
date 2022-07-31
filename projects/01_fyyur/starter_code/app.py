#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import sys
from tracemalloc import start
import dateutil.parser
import babel
from flask import Flask, jsonify, render_template, request, Response, flash, redirect, url_for
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy import ForeignKey
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

venue_genres = db.Table('venue_genres',
  db.Column('venue_id', db.Integer, db.ForeignKey('venue.id'), primary_key=True),
  db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True)
)

artist_genres = db.Table('artist_genres',
  db.Column('artist_id', db.Integer, db.ForeignKey('artist.id'), primary_key=True),
  db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True)
)

# shows = db.Table('shows',
#   db.Column('venue_id', db.Integer, db.ForeignKey('venue.id'), primary_key=True),
#   db.Column('artist_id', db.Integer, db.ForeignKey('artist.id'), primary_key=True),
#   db.Column('start_time', db.DateTime, primary_key=True))

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.relationship('Genre', secondary=venue_genres, backref=db.backref('venues', lazy=True))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref=db.backref('venue'))
    # artists = db.relationship('Artist', secondary=shows, backref=db.backref('venues', lazy=True))
    # past_shows - I think this is a many-to-many, should be calc by date
    # upcoming_shows - Same again
    # past_shows_count - should be calculated
    # upcoming_shows_count - should be calculated

    def __repr__(self):
      return f'<Venue ID: {self.id}, Name: {self.name}, Genres: {self.genres}, City: {self.city}, State: {self.state}, Address: {self.address}, Phone: {self.phone}, Image Link: {self.image_link}, Facebook Link: {self.facebook_link}, Website: {self.website}, Seeking Talent?: {self.seeking_talent}, Seeking Description: {self.seeking_description}>'
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.relationship('Genre', secondary=artist_genres, backref=db.backref('artists', lazy=True))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    #venues = db.relationship('Show', backref=db.backref('artist'))
    # past_shows - I think this is a many-to-many, should be calc by date
    # upcoming_shows - Same again
    # past_shows_count - should be calculated
    # upcoming_shows_count - should be calculated

    def __repr__(self):
      return f'<Artist ID: {self.id}, Name: {self.name}, Genres: {self.genres}, City: {self.city}, State: {self.state}, Phone: {self.phone}, Image Link: {self.image_link}, Facebook Link: {self.facebook_link}, Website: {self.website}, Seeking Venue?: {self.seeking_venue}, Seeking Description: {self.seeking_description}>'
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Genre(db.Model):
    __tablename__ = 'genre'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)

    def __repr__(self):
      return f'<Genre ID: {self.id}, Name: {self.name}>'

class Show(db.Model):
  __tablename__ = 'shows'
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), primary_key=True)
  start_time = db.Column(db.DateTime, primary_key=True)
  artist = db.relationship('Artist', backref=db.backref('shows'))
  # venue = db.relationship('Venue', backref=db.backref('artists'))

  def __init__(self, venue, artist, start_time):
    self.venue_id = venue.id
    self.artist_id = artist.id
    self.start_time = start_time
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  # Create dicts for each city and state combo
  data = []
  venues = Venue.query.distinct(Venue.city, Venue.state)
  for venue in venues:
    data.append({
      "city": venue.city,
      "state": venue.state,
      "venues": []
    })
  
  for venue in Venue.query.all():
    for d in data:
      if d['city'] == venue.city and d['state'] == venue.state:
        d['venues'].append({
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": len([show for show in venue.shows if show.start_time > datetime.now()])
        })
  
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  today_datetime = datetime.now()
  # We need to get a list of past shows and upcoming shows
  past_shows = []
  upcoming_shows = []

  all_show_rows = venue.shows
  for show in all_show_rows:
    if show.start_time < today_datetime:
      past_shows.append({
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time.isoformat()
      })
    else:
      upcoming_shows.append({
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time.isoformat()
      })
  
  

  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": [x.name for x in venue.genres],
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
    }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False

  # Check whether genre with name exists, else create a new genre
  genres= []
  for name in request.form.getlist('genres'):
    genre = Genre.query.filter_by(name=name).first()
    if genre:
      genres.append(genre)
    else:
      genres.append(Genre(name=name))

  try:
    # Extract all properties from the form
    name= request.form['name']
    city = request.form['city']
    state = request.form['state']
    address =request.form['address']
    phone = request.form['phone']
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    website_link= request.form['website_link']
    seeking_talent = True if 'seeking_talent' in request.form else False
    seeking_description= request.form['seeking_description']
    
    # Create a Venue model
    venue = Venue(name=name, city=city, state=state, address=address, phone=phone, image_link=image_link, genres=genres, facebook_link=facebook_link,website=website_link, seeking_talent=seeking_talent, seeking_description=seeking_description)

    # Commit Venue to database
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred. Venue ' + name + ' could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Venue ' + name + ' was successfully listed!')
  
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = []
  for artist in Artist.query.all():
    data.append({
      "id": artist.id,
      "name": artist.name,
    })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)
  today_datetime = datetime.now()
  # We need to get a list of past shows and upcoming shows
  past_shows = []
  upcoming_shows = []

  all_show_rows = artist.shows
  for show in all_show_rows:
    if show.start_time < today_datetime:
      past_shows.append({
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "venue_image_link": show.venue.image_link,
        "start_time": show.start_time.isoformat()
      })
    else:
      upcoming_shows.append({
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "venue_image_link": show.venue.image_link,
        "start_time": show.start_time.isoformat()
      })
  
  data={
    "id": artist.id,
    "name": artist.name,
    "genres": [x.name for x in artist.genres],
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue_row = Venue.query.get(venue_id)
  venue={
    "id": venue_row.id,
    "name": venue_row.name,
    "genres": [x.name for x in venue_row.genres],
    "address": venue_row.address,
    "city": venue_row.city,
    "state": venue_row.state,
    "phone": venue_row.phone,
    "website": venue_row.website,
    "facebook_link": venue_row.facebook_link,
    "seeking_talent": venue_row.seeking_talent,
    "seeking_description": venue_row.seeking_description,
    "image_link": venue_row.image_link
  }
  
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False

  # Check whether genre with name exists, else create a new genre
  genres= []
  for name in request.form.getlist('genres'):
    genre = Genre.query.filter_by(name=name).first()
    if genre:
      genres.append(genre)
    else:
      genres.append(Genre(name=name))

  try:
    venue = Venue.query.get(venue_id)
    venue.name = request.form['name']
    venue.genres = genres
    venue.address =request.form['address']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.phone = request.form['phone']
    venue.website = request.form['website_link']
    venue.facebook_link = request.form['facebook_link']
    venue.seeking_talent = True if 'seeking_talent' in request.form else False
    venue.seeking_description = request.form['seeking_description']
    venue.image_link = request.form['image_link']

    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    # flash('An error occurred. Venue ' + venue.name + ' could not be edited.')
    print("success")
  else:
    # on successful db insert, flash success
    # flash('Venue ' + venue.name + ' was successfully listed!')
    print("error")
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False

  # Check whether genre with name exists, else create a new genre
  genres= []
  for name in request.form.getlist('genres'):
    genre = Genre.query.filter_by(name=name).first()
    if genre:
      genres.append(genre)
    else:
      genres.append(Genre(name=name))
  
  try:
    # Extract all properties from the form
    name= request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    website_link= request.form['website_link']
    seeking_venue = True if 'seeking_venue' in request.form else False
    seeking_description= request.form['seeking_description']
    
    # Create an Artist model
    artist = Artist(name=name, city=city, state=state, phone=phone, image_link=image_link, genres=genres, facebook_link=facebook_link,website=website_link, seeking_venue=seeking_venue, seeking_description=seeking_description)

    # Commit Artist to database
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    flash('An error occurred. Artist ' + name + ' could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Artist ' + name + ' was successfully listed!')

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []
  for show in Show.query.all():
    data.append({
      "venue_id": show.venue.id,
      "venue_name": show.venue.name,
      "artist_id": show.artist.id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.isoformat()
    })
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False

  try:
    artist_id = int(request.form['artist_id'])
    venue_id = int(request.form['venue_id'])
    start_time = dateutil.parser.parse(request.form['start_time'])

    venue = Venue.query.get(venue_id)
    artist = Artist.query.filter_by(id=artist_id).first()
    show = Show(venue, artist, start_time)
    show.artist = artist
    # #show.venue = venue
    venue.shows.append(show)

    # # Commit the amended venue to the datbase
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred. Show could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
