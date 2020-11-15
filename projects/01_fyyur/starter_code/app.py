#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import datetime, sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app    = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db     = SQLAlchemy(app)

# TODO: connect to a local postgresql database
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

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]
  # return render_template('pages/venues.html', areas=data);

  try:
    # main data list wrapper.
    states_and_cities = []
    # the db venues query.
    venues = Venue.query.distinct(Venue.state, Venue.city).all()
    # wrap states and cities dict inside the main list wrapper.
    for venue in venues:
      states_and_cities.append({
        "state": venue.state,
        "city": venue.city
      })

    # loop through each city.
    for state_and_city in states_and_cities:
      # the city based venues query.
      city_venues = Venue.query.filter_by(city=state_and_city['city']).all()
      # the city based venues wrapper.
      final_result = []
      # wrap the city venues inside the list wrapper.
      for city_venue in city_venues:
        final_result.append({
          "id"                : city_venue.id,
          "name"              : city_venue.name,
          "num_upcoming_shows": len(city_venue.shows)
        })
      state_and_city['venues'] = final_result

    return render_template('pages/venues.html', areas=states_and_cities)
  except:
    flash('Oops, Something went wrong')
    return redirect(url_for('index'))

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # search for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  # return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

  try:
    # stripped searching input value.
    search_term = request.form.get('search_term').strip()

    # retrieve venues data of the value entered regardless the case sensitivity.
    venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
    # the matched venues dict with a key of the venues count.
    response = {"count": len(venues)}
    # the venues data list wrapper.
    response_data = []
    # wrap data within the list.
    for venue in venues:
      data = {
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": len(venue.shows)
      }
      response_data.append(data)

    # update the matched venue dict with a key of its required data.
    response.update({
      "data": response_data
    })
    return render_template('pages/search_venues.html', results=response, search_term=search_term)
  except:
    flash('Oops, Something went wrong')
    return redirect(url_for('venues'))
  

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  # data1={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #   "past_shows": [{
  #     "artist_id": 4,
  #     "artist_name": "Guns N Petals",
  #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 2,
  #   "name": "The Dueling Pianos Bar",
  #   "genres": ["Classical", "R&B", "Hip-Hop"],
  #   "address": "335 Delancey Street",
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "914-003-1132",
  #   "website": "https://www.theduelingpianos.com",
  #   "facebook_link": "https://www.facebook.com/theduelingpianos",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 3,
  #   "name": "Park Square Live Music & Coffee",
  #   "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
  #   "address": "34 Whiskey Moore Ave",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "415-000-1234",
  #   "website": "https://www.parksquarelivemusicandcoffee.com",
  #   "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #   "past_shows": [{
  #     "artist_id": 5,
  #     "artist_name": "Matt Quevedo",
  #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [{
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 1,
  # }
  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  # return render_template('pages/show_venue.html', venue=data)

  try:
    # the db venue query.
    venue = Venue.query.get(venue_id)
    # the venue main data.
    data  = {
      "id"                 : venue.id,
      "name"               : venue.name,
      "genres"             : venue.genres,
      "city"               : venue.city,
      "state"              : venue.state,
      "address"            : venue.address,
      "phone"              : venue.phone,
      "image_link"         : venue.image_link,
      "facebook_link"      : venue.facebook_link,
      "website"            : venue.website,
      "seeking_talent"     : venue.seeking_talent,
      "seeking_description": venue.seeking_description
    }

    # the db venue's past shows query.
    venue_past_shows = Show.query.filter(Show.venue_id == venue.id, Show.time_start < datetime.datetime.now()).all()
    # the past shows list wrapper.
    past_shows       = []
    # wrap each past show dict within the list wrapper.
    for venue_past_show in venue_past_shows:
      past_show_data = {
        "start_time"       : venue_past_show.time_start.strftime('%A %b, %d, %Y at %I:%M%p'),
        "artist_id"        : venue_past_show.artist_id,
        "artist_name"      : venue_past_show.artist.name,
        "artist_image_link": venue_past_show.artist.image_link
      }
      past_shows.append(past_show_data)
    
    # update the venue's main data dict with a new key of past shows
    data.update({
      'past_shows': past_shows
    })

    # the db venue's upcoming shows query.
    venue_upcoming_shows = Show.query.filter(Show.venue_id == venue.id, Show.time_start > datetime.datetime.now()).all()
    # the upcoming shows list wrapper.
    upcoming_shows       = []
    # wrap each upcoming show dict within the list wrapper.
    for venue_upcoming_show in venue_upcoming_shows:
      upcoming_show_data = {
        "start_time"       : venue_upcoming_show.time_start.strftime('%A %b, %d, %Y at %I:%M%p'),
        "artist_id"        : venue_upcoming_show.artist_id,
        "artist_name"      : venue_upcoming_show.artist.name,
        "artist_image_link": venue_upcoming_show.artist.image_link
      }
      upcoming_shows.append(upcoming_show_data)
    
    # update the venue's main data dict with new keys of upcoming shows, past shows count, and upcoming shows count.
    data.update({
      'upcoming_shows'      : upcoming_shows,
      "past_shows_count"    : len(past_shows),
      "upcoming_shows_count": len(upcoming_shows),
    })

    return render_template('pages/show_venue.html', venue=data)
  except:
    flash('Oops, Something went wrong')
    return redirect(url_for('index'))

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

  # initiate error equal to false.
  error = False
  try:
    # create new venue instace with the request data.
    venue = Venue(
      name           = request.form['name'],
      city           = request.form['city'],
      state          = request.form['state'],
      address        = request.form['address'],
      phone          = request.form['phone'],
      genres         = request.form.getlist('genres'),
      website        = request.form['website'],
      image_link     = request.form['image_link'],
      facebook_link  = request.form['facebook_link'],
      seeking_talent = bool(request.form['seeking_talent'] == 'True')
    )
    # add the new created instance to the session.
    db.session.add(venue)
    # commet changes occurred to db.
    db.session.commit()
  except:
    # rollback all the session changes if any exception occurred.
    db.session.rollback()
    # display the system inforamation of execution.
    print(sys.exc_info())
    # update the error status to be true.
    error = True
  finally:
    # close the db session.
    db.session.close()
  if error == True:
    flash(f'Oops, An error occurred. Venue "{venue.name}" could not be listed.')
  else:
    flash('Congrats: Venue "' + request.form['name'] + '" was successfully listed!')
  return render_template('pages/home.html')

  # on successful db insert, flash success
  # flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  # return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # initiate error equals false.
  error = False
  try:
    # the db query of deleting a venue of an id.
    Venue.query.filter_by(id=venue_id).delete()
    # commit changes to the db.
    db.session.commit()
  except:
    # rollback all the session changes if any exception occurred.
    db.session.rollback()
    # display the system inforamation of execution.
    print(sys.exc_info())
    # update the error status to be true.
    error = True
  finally:
    # close the db session.
    db.session.close()
  if error == True:
    # flash(f'Oops, An error occurred. The venue of ID "{venue_id}" could not be deleted.')
    abort(500)
  else:
    flash(f'Congrats: The venue of ID "{venue_id}" was successfully deleted!')
  # return render_template('pages/home.html')
  return jsonify({'success': True})

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]
  
  try:
    # the db artists query.
    artists = Artist.query.all()
    # the required data wrapper.
    data = []
    # wrap data inside the list wrapper.
    for artist in artists:
      data.append({
        'id'  : artist.id,
        'name': artist.name
      })
  
    return render_template('pages/artists.html', artists=data)
  except:
    flash('Oops, Something went wrong.')
    return redirect(url_for('index'))

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # search for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  # return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

  try:
    # stripped searching input value.
    search_term = request.form.get('search_term').strip()

    # retrieve artists data of the value entered regardless the case sensitivity.
    artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
    # the matched artists dict with a key of the artists count.
    response = {"count": len(artists)}
    # the artists data list wrapper.
    response_data = []
    # wrap data within the list.
    for artist in artists:
      data = {
        "id": artist.id,
        "name": artist.name,
        "num_upcoming_shows": len(artist.shows)
      }
      response_data.append(data)

    # update the matched artist dict with a key of its required data.
    response.update({
      "data": response_data
    })
    return render_template('pages/search_artists.html', results=response, search_term=search_term)
  except:
    flash('Oops, Something went wrong')
    return redirect(url_for('artists'))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  # data1={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 5,
  #   "name": "Matt Quevedo",
  #   "genres": ["Jazz"],
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "300-400-5000",
  #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "past_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  #   "genres": ["Jazz", "Classical"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "432-325-5432",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 3,
  # }
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  # return render_template('pages/show_artist.html', artist=data)

  try:
    # the db artist query.
    artist = Artist.query.get(artist_id)
    # the artist main data.
    data  = {
      "id"                 : artist.id,
      "name"               : artist.name,
      "city"               : artist.city,
      "state"              : artist.state,
      "phone"              : artist.phone,
      "genres"             : artist.genres,
      "image_link"         : artist.image_link,
      "facebook_link"      : artist.facebook_link,
      "website"            : artist.website,
      "seeking_venue"      : artist.seeking_venue,
      "seeking_description": artist.seeking_description
    }

    # the db artist's past shows query.
    artist_past_shows = Show.query.filter(Show.artist_id == artist.id, Show.time_start < datetime.datetime.now()).all()
    # the past shows list wrapper.
    past_shows       = []
    # wrap each past show dict within the list wrapper.
    for artist_past_show in artist_past_shows:
      past_show_data = {
        "start_time"      : artist_past_show.time_start.strftime('%A %b, %d, %Y at %I:%M%p'),
        "venue_id"        : artist_past_show.venue_id,
        "venue_name"      : artist_past_show.venue.name,
        "venue_image_link": artist_past_show.venue.image_link
      }
      past_shows.append(past_show_data)
    
    # update the artist's main data dict with a new key of past shows
    data.update({
      'past_shows': past_shows
    })

    # the db artist's upcoming shows query.
    artist_upcoming_shows = Show.query.filter(Show.artist_id == artist.id, Show.time_start > datetime.datetime.now()).all()
    # the upcoming shows list wrapper.
    upcoming_shows       = []
    # wrap each upcoming show dict within the list wrapper.
    for artist_upcoming_show in artist_upcoming_shows:
      upcoming_show_data = {
        "start_time"      : artist_upcoming_show.time_start.strftime('%A %b, %d, %Y at %I:%M%p'),
        "venue_id"        : artist_upcoming_show.venue_id,
        "venue_name"      : artist_upcoming_show.venue.name,
        "venue_image_link": artist_upcoming_show.venue.image_link
      }
      upcoming_shows.append(upcoming_show_data)
    
    # update the artist's main data dict with new keys of upcoming shows, past shows count, and upcoming shows count.
    data.update({
      'upcoming_shows'      : upcoming_shows,
      "past_shows_count"    : len(past_shows),
      "upcoming_shows_count": len(upcoming_shows),
    })

    return render_template('pages/show_artist.html', artist=data)
  except:
    flash('Oops, Something went wrong')
    print(sys.exc_info())
    return redirect(url_for('index'))

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # form = ArtistForm()
  # artist={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }
  # TODO: populate form with fields from artist with ID <artist_id>
  try:
    artist = Artist.query.get(artist_id)
    form = ArtistForm(
      name          = artist.name,
      genres        = artist.genres,
      city          = artist.city,
      state         = artist.state,
      phone         = artist.phone,
      facebook_link = artist.facebook_link,
      website       = artist.website,
      seeking_venue = artist.seeking_venue,
      image_link    = artist.image_link
    )
    return render_template('forms/edit_artist.html', form=form, artist=artist)
  except:
    flash('Oops, Something went wrong')
    return redirect(url_for('index'))

@app.route('/artists/<int:artist_id>/update', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  
  # initiate error equal to false.
  error = False
  try:
    # update artist instace with the request data.
    Artist.query.filter_by(id=artist_id).update({
      'name'          : request.form.get('name'),
      'city'          : request.form.get('city'),
      'state'         : request.form.get('state'),
      'phone'         : request.form.get('phone'),
      'genres'        : request.form.getlist('genres'),
      'website'       : request.form.get('website'),
      'image_link'    : request.form.get('image_link'),
      'facebook_link' : request.form.get('facebook_link'),
      'seeking_venue' : bool(request.form.get('seeking_venue') == 'True')
    })
    # commet changes occurred to db.
    db.session.commit()
  except:
    # rollback all the session changes if any exception occurred.
    db.session.rollback()
    # display the system inforamation of execution.
    print(sys.exc_info())
    # update the error status to be true.
    error = True
  finally:
    # close the db session.
    db.session.close()
  if error == True:
    flash('Oops, An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
  else:
    flash('Congrats: Artist ' + request.form['name'] + ' has been successfully updated!')
    
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # form = VenueForm()
  # venue={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  # }
  # return render_template('forms/edit_venue.html', form=form, venue=venue)
  # TODO: populate form with values from venue with ID <venue_id>
  try:
    venue = Venue.query.get(venue_id)
    form = VenueForm(
      name           = venue.name,
      genres         = venue.genres,
      city           = venue.city,
      state          = venue.state,
      address        = venue.address,
      phone          = venue.phone,
      facebook_link  = venue.facebook_link,
      website        = venue.website,
      seeking_talent = venue.seeking_talent,
      image_link     = venue.image_link
    )
    return render_template('forms/edit_venue.html', form=form, venue=venue)
  except:
    flash('Oops, Something went wrong')
    print(sys.exc_info())
    return redirect(url_for('index'))

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  # return redirect(url_for('show_venue', venue_id=venue_id))

  # initiate error equal to false.
  error = False
  try:
    # update venue instace with the request data.
    Venue.query.filter_by(id=venue_id).update({
      'name'          : request.form.get('name'),
      'city'          : request.form.get('city'),
      'state'         : request.form.get('state'),
      'address'       : request.form.get('address'),
      'phone'         : request.form.get('phone'),
      'genres'        : request.form.getlist('genres'),
      'website'       : request.form.get('website'),
      'image_link'    : request.form.get('image_link'),
      'facebook_link' : request.form.get('facebook_link'),
      'seeking_talent': bool(request.form.get('seeking_talent') == 'True')
    })
    # commet changes occurred to db.
    db.session.commit()
  except:
    # rollback all the session changes if any exception occurred.
    db.session.rollback()
    # display the system inforamation of execution.
    print(sys.exc_info())
    # update the error status to be true.
    error = True
  finally:
    # close the db session.
    db.session.close()
  if error == True:
    flash('Oops, An error occurred. Venue "' + request.form['name'] + '" could not be updated.')
  else:
    flash('Congrats: Venue "' + request.form['name'] + '" has been successfully updated!')
    
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

  # on successful db insert, flash success
  # flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  # return render_template('pages/home.html')
  
  # initiate error equal to false.
  error = False
  try:
    # create new artist instace with the request data.
    artist = Artist(
      name          = request.form['name'],
      city          = request.form['city'],
      state         = request.form['state'],
      phone         = request.form['phone'],
      genres        = request.form.getlist('genres'),
      website       = request.form['website'],
      image_link    = request.form['image_link'],
      facebook_link = request.form['facebook_link'],
      seeking_venue = bool(request.form['seeking_venue'] == 'True')
    )
    # add the new created instance to the session.
    db.session.add(artist)
    # commet changes occurred to db.
    db.session.commit()
  except:
    # rollback all the session changes if any exception occurred.
    db.session.rollback()
    # display the system inforamation of execution.
    print(sys.exc_info())
    # update the error status to be true.
    error = True
  finally:
    # close the db session.
    db.session.close()
  if error == True:
    flash(f'Oops, An error occurred. Artist "{artist.name}" could not be listed.')
  else:
    flash('Congrats: Artist "' + request.form['name'] + '" was successfully listed!')
  return render_template('pages/home.html')

@app.route('/artists/<artist_id>/delete', methods=['DELETE'])
def delete_artist(artist_id):
  # TODO: Complete this endpoint for taking a artist_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # initiate error equals false.
  error = False
  try:
    # the db query of deleting a artist of an id.
    Artist.query.filter_by(id=artist_id).delete()
    # commit changes to the db.
    db.session.commit()
  except:
    # rollback all the session changes if any exception occurred.
    db.session.rollback()
    # display the system inforamation of execution.
    print(sys.exc_info())
    # update the error status to be true.
    error = True
  finally:
    # close the db session.
    db.session.close()
  if error == True:
    # flash(f'Oops, An error occurred. The artist of ID "{artist_id}" could not be deleted.')
    abort(500)
  else:
    flash(f'Congrats: The artist of ID "{artist_id}" was successfully deleted!')
  # return render_template('pages/home.html')
  return jsonify({'success': True})


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  # data=[{
  #   # "venue_id": 1,
  #   "venue_id": 8,
  #   "venue_name": "The Musical Hop",
  #   # "artist_id": 4,
  #   "artist_id": 5,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   # "venue_id": 3,
  #   "venue_id": 10,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   # "artist_id": 5,
  #   "artist_id": 6,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   # "venue_id": 3,
  #   "venue_id": 10,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   # "artist_id": 6,
  #   "artist_id": 7,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   # "venue_id": 3,
  #   "venue_id": 10,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   # "artist_id": 6,
  #   "artist_id": 7,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   # "venue_id": 3,
  #   "venue_id": 10,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   # "artist_id": 6,
  #   "artist_id": 7,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]
  # return render_template('pages/shows.html', shows=data)

  try:
    # the db shows query.
    shows = Show.query.all()
    # the show main data wrapper.
    data  = []
    # wrap show data into the predefined wrapper.
    for show in shows:
      data.append({
        "venue_id"         : show.venue_id,
        "venue_name"       : show.venue.name,
        "artist_id"        : show.artist_id,
        "artist_name"      : show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time"       : show.time_start.strftime('%A %b, %d, %Y at %I:%M%p')
      })
    return render_template('pages/shows.html', shows=data)
  except:
    flash('Oops, Something went wrong')
    print(sys.exc_info())
    return redirect(url_for('index'))


@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  # flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  # return render_template('pages/home.html')

  # initiate error equal to false.
  error = False
  try:
    # request venue id value.
    venue_id   = int(request.form.get('venue_id'))
    # request artist id value.
    artist_id  = int(request.form.get('artist_id'))
    # request start time value with the hint format check.
    start_time = datetime.datetime.strptime(request.form.get('start_time'),'%Y-%m-%d %I:%M:%S').strftime('%Y-%m-%d %I:%M:%S')
    # the db venue id existence query.
    venue_id_exists  = bool(Venue.query.filter_by(id=venue_id).first())
    # the db artist id existence query.
    artist_id_exists = bool(Artist.query.filter_by(id=artist_id).first())
    # check whether venue id and artist id have physical existence into the db.
    if not venue_id_exists or not artist_id_exists:
      flash('Please enter a valid ID value')
      return redirect(url_for('create_shows'))

    # create new show instace with the request data.
    show = Show(
      time_start = start_time,
      venue_id   = venue_id,
      artist_id  = artist_id
    )
    # add the new created instance to the session.
    db.session.add(show)
    # commet changes occurred to db.
    db.session.commit()
  except:
    if ValueError:
      # rollback all the session changes if any exception occurred.
      db.session.rollback()
      print(sys.exc_info())
      flash('Please enter a valid start time value as hinted.')
      return redirect(url_for('create_shows'))
    else:
      # rollback all the session changes if any exception occurred.
      db.session.rollback()
      # display the system inforamation of execution.
      print(sys.exc_info())
      # update the error status to be true.
      error = True
  finally:
    # close the db session.
    db.session.close()
  if error == True:
    flash(f'Oops, An error occurred. the show of date: "{start_time}" could not be listed.')
  else:
    flash(f'Congrats, the show of date: "{start_time}" was successfully listed!')
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
