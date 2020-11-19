#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
  Flask,
  render_template,
  request,
  Response,
  flash,
  redirect,
  url_for,
  jsonify
)
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from datetime import datetime
import sys
from models import app, db, Venue, Artist, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

moment = Moment(app)
db.init_app(app)

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
  try:
    venues = Venue.query.all()
    locals = [
      {
        'city': place.city,
        'state': place.state,
        'venues': [{
            'id': venue.id,
            'name': venue.name,
        } for venue in venues if
            venue.city == place.city and venue.state == place.state]
      } for place in Venue.query.distinct(Venue.city, Venue.state).all()]

    return render_template('pages/venues.html', areas=locals)
  except:
    flash('Oops, Something went wrong')
    return redirect(url_for('index'))

@app.route('/venues/search', methods=['POST'])
def search_venues():
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
  try:
    past_shows = db.session.query(
      Artist,
      Show
    ).join(Show).join(Venue).filter(
        Show.venue_id  == venue_id,
        Show.artist_id == Artist.id,
        Show.time_start < datetime.now()
    ).all()
    
    upcoming_shows = db.session.query(
      Artist,
      Show
    ).join(Show).join(Venue).filter(
        Show.venue_id  == venue_id,
        Show.artist_id == Artist.id,
        Show.time_start > datetime.now()
    ).all()

    venue = Venue.query.filter_by(id=venue_id).first_or_404()
    data = {
        'id'                 : venue.id,
        'name'               : venue.name,
        'genres'             : venue.genres,
        'city'               : venue.city,
        'state'              : venue.state,
        'address'            : venue.address,
        'phone'              : venue.phone,
        'image_link'         : venue.image_link,
        'facebook_link'      : venue.facebook_link,
        'website'            : venue.website,
        'seeking_talent'     : venue.seeking_talent,
        'seeking_description': venue.seeking_description,
        'past_shows': [{
            'artist_id'        : artist.id,
            'artist_name'      : artist.name,
            'artist_image_link': artist.image_link,
            'start_time'       : show.time_start.strftime('%A %b, %d, %Y at %I:%M%p')
        } for artist, show in past_shows],
        'upcoming_shows': [{
            'artist_id'        : artist.id,
            'artist_name'      : artist.name,
            'artist_image_link': artist.image_link,
            'start_time'       : show.time_start.strftime('%A %b, %d, %Y at %I:%M%p')
        } for artist, show in upcoming_shows],
        'past_shows_count'    : len(past_shows),
        'upcoming_shows_count': len(upcoming_shows)
    }

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
  # validate the form inputs
  # -------------------------------------------------
  # note that: seeking_description is stored by default as static string value
  # if a user selects yes value for seeking_talent the seeking description
  # would be displayed inside the show page otherwise it wouldn't.
  # -------------------------------------------------
  form  = VenueForm(request.form, meta={'csrf': False})
  if form.validate():
    # initiate error equal to false.
    error = False
    try:
      # create new venue instace with the request data.
      venue = Venue(
        name           = form.data['name'],
        city           = form.data['city'],
        state          = form.data['state'],
        address        = form.data['address'],
        phone          = form.data['phone'],
        genres         = form.data['genres'],
        website        = form.data['website'],
        image_link     = form.data['image_link'],
        facebook_link  = form.data['facebook_link'],
        seeking_talent = bool(form.data['seeking_talent'] == 'True')
      )
      # add the new created instance to the session.
      db.session.add(venue)
      # commet changes occurred to db.
      db.session.commit()
    except ValueError as e:
      db.session.rollback()
      print(e)
      print(sys.exc_info())
      flash("Oops, Values don't match database columns")
      error = True
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
  else:
    messages = [f'{field} | {error}' for field, error in form.errors.items()]
    for message in messages:
      error_index       = message.find('|')+2
      error_message     = message[error_index:].lstrip('[').rstrip(']').strip("'")
      field_message     = message[:error_index].replace('_', ' ')
      formatted_message = (field_message + error_message).replace('|', '').replace("'", "").replace(".", "")
      flash(f'Error: {formatted_message}')
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
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

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  try:
    # the db artists query.
    artists = Artist.query.all()
    # the required data wrapper.
    data = [{
        'id'  : artist.id,
        'name': artist.name
      } for artist in artists]

    return render_template('pages/artists.html', artists=data)
  except:
    flash('Oops, Something went wrong.')
    return redirect(url_for('index'))

@app.route('/artists/search', methods=['POST'])
def search_artists():
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
  try:
    past_shows = db.session.query(
      Venue,
      Show
    ).join(Show).join(Artist).filter(
        Show.venue_id  == Venue.id,
        Show.artist_id == artist_id,
        Show.time_start < datetime.now()
    ).all()
    
    upcoming_shows = db.session.query(
      Venue,
      Show
    ).join(Show).join(Artist).filter(
        Show.venue_id  == Venue.id,
        Show.artist_id == artist_id,
        Show.time_start > datetime.now()
    ).all()

    artist = Artist.query.filter_by(id=artist_id).first_or_404()
    data = {
        'id'                 : artist.id,
        'name'               : artist.name,
        'genres'             : artist.genres,
        'city'               : artist.city,
        'state'              : artist.state,
        'phone'              : artist.phone,
        'image_link'         : artist.image_link,
        'facebook_link'      : artist.facebook_link,
        'website'            : artist.website,
        'seeking_venue'      : artist.seeking_venue,
        'seeking_description': artist.seeking_description,
        'past_shows': [{
            'venue_id'        : venue.id,
            'venue_name'      : venue.name,
            'venue_image_link': venue.image_link,
            'start_time'      : show.time_start.strftime('%A %b, %d, %Y at %I:%M%p')
        } for venue, show in past_shows],
        'upcoming_shows': [{
            'venue_id'        : venue.id,
            'venue_name'      : venue.name,
            'venue_image_link': venue.image_link,
            'start_time'      : show.time_start.strftime('%A %b, %d, %Y at %I:%M%p')
        } for venue, show in upcoming_shows],
        'past_shows_count'    : len(past_shows),
        'upcoming_shows_count': len(upcoming_shows)
    }

    return render_template('pages/show_artist.html', artist=data)
  except:
    flash('Oops, Something went wrong')
    print(sys.exc_info())
    return redirect(url_for('index'))

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
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
  
  # validate the form inputs
  # -------------------------------------------------
  # note that: seeking_description is stored by default as static string value
  # if a user selects yes value for seeking_venue the seeking description
  # would be displayed inside the show page otherwise it wouldn't.
  # -------------------------------------------------
  form  = ArtistForm(request.form, meta={'csrf': False})
  if form.validate():
    # initiate error equal to false.
    error = False
    try:
      # update artist instace with the request data.
      Artist.query.filter_by(id=artist_id).update({
        'name'          : form.data['name'],
        'city'          : form.data['city'],
        'state'         : form.data['state'],
        'phone'         : form.data['phone'],
        'genres'        : form.data['genres'],
        'website'       : form.data['website'],
        'image_link'    : form.data['image_link'],
        'facebook_link' : form.data['facebook_link'],
        'seeking_venue' : bool(form.data['seeking_venue'] == 'True')
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
  else:
    messages = [f'{field} | {error}' for field, error in form.errors.items()]
    for message in messages:
      error_index       = message.find('|')+2
      error_message     = message[error_index:].lstrip('[').rstrip(']').strip("'")
      field_message     = message[:error_index].replace('_', ' ')
      formatted_message = (field_message + error_message).replace('|', '').replace("'", "").replace(".", "")
      flash(f'Error: {formatted_message}')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
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

@app.route('/venues/<int:venue_id>/update', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  
  # validate the form inputs
  # -------------------------------------------------
  # note that: seeking_description is stored by default as static string value
  # if a user selects yes value for seeking_talent the seeking description
  # would be displayed inside the show page otherwise it wouldn't.
  # -------------------------------------------------
  form  = VenueForm(request.form, meta={'csrf': False})
  if form.validate():
    # initiate error equal to false.
    error = False
    try:
      # update venue instace with the request data.
      Venue.query.filter_by(id=venue_id).update({
        'name'          : form.data['name'],
        'city'          : form.data['city'],
        'state'         : form.data['state'],
        'address'       : form.data['address'],
        'phone'         : form.data['phone'],
        'genres'        : form.data['genres'],
        'website'       : form.data['website'],
        'image_link'    : form.data['image_link'],
        'facebook_link' : form.data['facebook_link'],
        'seeking_talent': bool(form.data['seeking_talent'] == 'True')
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
  else:
    messages = [f'{field} | {error}' for field, error in form.errors.items()]
    for message in messages:
      error_index       = message.find('|')+2
      error_message     = message[error_index:].lstrip('[').rstrip(']').strip("'")
      field_message     = message[:error_index].replace('_', ' ')
      formatted_message = (field_message + error_message).replace('|', '').replace("'", "").replace(".", "")
      flash(f'Error: {formatted_message}')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # validate the form inputs
  # -------------------------------------------------
  # note that: seeking_description is stored by default as static string value
  # if a user selects yes value for seeking_venue the seeking description
  # would be displayed inside the show page otherwise it wouldn't.
  # -------------------------------------------------
  form  = ArtistForm(request.form, meta={'csrf': False})
  if form.validate():
    # initiate error equal to false.
    error = False
    try:
      # create new artist instace with the request data.
      artist = Artist(
        name           = form.data['name'],
        city           = form.data['city'],
        state          = form.data['state'],
        phone          = form.data['phone'],
        genres         = form.data['genres'],
        website        = form.data['website'],
        image_link     = form.data['image_link'],
        facebook_link  = form.data['facebook_link'],
        seeking_venue  = bool(form.data['seeking_venue'] == 'True')
      )
      # add the new created instance to the session.
      db.session.add(artist)
      # commet changes occurred to db.
      db.session.commit()
    except ValueError as e:
      db.session.rollback()
      print(e)
      print(sys.exc_info())
      flash("Oops, Values don't match database columns")
      error = True
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
  else:
    messages = [f'{field} | {error}' for field, error in form.errors.items()]
    for message in messages:
      error_index       = message.find('|')+2
      error_message     = message[error_index:].lstrip('[').rstrip(']').strip("'")
      field_message     = message[:error_index].replace('_', ' ')
      formatted_message = (field_message + error_message).replace('|', '').replace("'", "").replace(".", "")
      flash(f'Error: {formatted_message}')
  return render_template('pages/home.html')

@app.route('/artists/<artist_id>/delete', methods=['DELETE'])
def delete_artist(artist_id):
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
  try:
    # the db shows query.
    shows = Show.query.all()
    # the show main data wrapper.
    data  = [{
        "venue_id"         : show.venue_id,
        "venue_name"       : show.venue.name,
        "artist_id"        : show.artist_id,
        "artist_name"      : show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time"       : show.time_start.strftime('%A %b, %d, %Y at %I:%M%p')
      } for show in shows]
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
  form  = ShowForm(request.form, meta={'csrf': False})
  if form.validate():
    # initiate error equal to false.
    error = False
    try:
      # request venue id value.
      venue_id   = int(form.data['venue_id'])
      # request artist id value.
      artist_id  = int(form.data['artist_id'])
      # request start time value with the hint format check.
      # start_time = datetime.datetime.strptime(request.form.get('start_time'),'%Y-%m-%d %I:%M:%S').strftime('%Y-%m-%d %I:%M:%S')
      start_time = form.data['start_time']
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
  else:
    messages = [f'{field} | {error}' for field, error in form.errors.items()]
    for message in messages:
      error_index       = message.find('|')+2
      error_message     = message[error_index:].lstrip('[').rstrip(']').strip("'")
      field_message     = message[:error_index].replace('_', ' ')
      formatted_message = (field_message + error_message).replace('|', '').replace("'", "").replace(".", "")
      flash(f'Error: {formatted_message}')
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
