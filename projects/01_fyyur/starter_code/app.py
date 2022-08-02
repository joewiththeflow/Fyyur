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
from models import db, venue_genres, artist_genres, Venue, Artist, Genre, Show
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy import ForeignKey, func
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)

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
  
  # Loop through the venues and add to the correct city and state dict
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
  search_term = request.form.get('search_term', '')

  # Append Venues to data dict if the lower case search term is contained in the lower case Venue.name
  data = []
  for venue in Venue.query.filter(func.lower(Venue.name).contains(func.lower(search_term))):
    data.append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": len([show for show in venue.shows if show.start_time > datetime.now()]),
    })
  
  # Add the data dict to the response along with length of data dict
  response={
    "count": len(data),
    "data": data
  }
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  # Get the correct Venue and the current datetime
  venue = Venue.query.get(venue_id)
  today_datetime = datetime.now()

  # Create dicts to store lists of past shows and upcoming shows
  past_shows = []
  upcoming_shows = []

  # Loop through all shows, adding those before current datetime to past_shows, else to upcoming_shows
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
  
  # Update the data dict with Venue information and past_shows and upcoming_shows dicts
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

  # Check whether Genre with name exists, else create a new Genre
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
    phone = request.form['phone'] if request.form['phone'] else None
    image_link = request.form['image_link'] if request.form['image_link'] else None
    facebook_link = request.form['facebook_link'] if request.form['facebook_link'] else None
    website_link= request.form['website_link'] if request.form['website_link'] else None
    seeking_talent = True if 'seeking_talent' in request.form else None
    seeking_description= request.form['seeking_description'] if request.form['seeking_description'] else None
    
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

  error = False

  try:
    # Delete the Venue with the passed in id
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    print("error")
  else:
    print("success")

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

  # Have edited edit_venue.html with button and added script to main.html
  # We must return a response for a DELETE method
  return jsonify({'success': not(error)})


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  # Get all Artists from db
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
  search_term = request.form.get('search_term', '')

  # Append Artists to data dict if the lower case search term is contained in the lower case Artist.name
  data = []
  for artist in Artist.query.filter(func.lower(Artist.name).contains(func.lower(search_term))):
    data.append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": len([show for show in artist.shows if show.start_time > datetime.now()]),
    })
  
  # Add the data dict to the response along with length of data dict
  response={
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

  # Get the correct Artist and the current datetime
  artist = Artist.query.get(artist_id)
  today_datetime = datetime.now()

  # Create dicts to store lists of past shows and upcoming shows
  past_shows = []
  upcoming_shows = []

  # Loop through all shows, adding those before current datetime to past_shows, else to upcoming_shows
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
  
  # Update the data dict with Artist information and past_shows and upcoming_shows dicts
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
  # Get the Artist based on id
  artist_row = Artist.query.get(artist_id)

  # Create the form, passing in Artist as obj to prepopulate, passing in website for website_link form parameter mismatch
  form = ArtistForm(obj=artist_row, website_link=artist_row.website)

  # Override the genres in the form
  form.genres.data = [x.name for x in artist_row.genres]

  # Not sure we need all this
  artist={
    "id": artist_row.id,
    "name": artist_row.name,
    "genres": [x.name for x in artist_row.genres],
    "city": artist_row.city,
    "state": artist_row.state,
    "phone": artist_row.phone,
    "website": artist_row.website,
    "facebook_link": artist_row.facebook_link,
    "seeking_venue": artist_row.seeking_venue,
    "seeking_description": artist_row.seeking_description,
    "image_link": artist_row.image_link
  }
  
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  error = False

  # Check whether Genre with name exists, else create a new Genre
  genres= []
  for name in request.form.getlist('genres'):
    genre = Genre.query.filter_by(name=name).first()
    if genre:
      genres.append(genre)
    else:
      genres.append(Genre(name=name))

  try:
    # Update Artist with form field values
    artist = Artist.query.get(artist_id)
    artist.name = request.form['name']
    artist.genres = genres
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.website = request.form['website_link']
    artist.facebook_link = request.form['facebook_link']
    artist.seeking_venue = True if 'seeking_venue' in request.form else False
    artist.seeking_description = request.form['seeking_description']
    artist.image_link = request.form['image_link']

    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    print("error")
  else:
    print("success")

  return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # Get the Venue based on id
  venue_row = Venue.query.get(venue_id)

  # Create the form, passing in Venue as obj to prepopulate, passing in website for website_link form parameter mismatch
  form = VenueForm(obj=venue_row, website_link=venue_row.website)

  # Override the genres in the form
  form.genres.data = [x.name for x in venue_row.genres]

  # Not sure we need all this
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

  # Check whether Genre with name exists, else create a new Genre
  genres= []
  for name in request.form.getlist('genres'):
    genre = Genre.query.filter_by(name=name).first()
    if genre:
      genres.append(genre)
    else:
      genres.append(Genre(name=name))

  try:
    # Update Venue with form field values
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
    print("error")
  else:
    print("success")

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

  # Check whether Genre with name exists, else create a new Genre
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
    phone = request.form['phone'] if request.form['phone'] else None
    image_link = request.form['image_link'] if request.form['image_link'] else None
    facebook_link = request.form['facebook_link'] if request.form['facebook_link'] else None
    website_link= request.form['website_link'] if request.form['website_link'] else None
    seeking_venue = True if 'seeking_venue' in request.form else None
    seeking_description= request.form['seeking_description'] if request.form['seeking_description'] else None
    
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

  # Get all Shows from db
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
    # Get Show column values from form
    artist_id = int(request.form['artist_id'])
    venue_id = int(request.form['venue_id'])
    start_time = dateutil.parser.parse(request.form['start_time'])

    # Get Venue and Artist
    venue = Venue.query.get(venue_id)
    artist = Artist.query.filter_by(id=artist_id).first()

    # Create Show
    show = Show(venue, artist, start_time)

    # Add Artist to Show
    show.artist = artist

    # Add Show to Venue
    venue.shows.append(show)

    # Commit the Venue to the database
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
