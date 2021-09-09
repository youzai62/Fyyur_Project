#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from datetime import time
import json
import sys
import dateutil.parser
import babel
from flask import render_template, request, Response, flash, redirect, url_for, abort, jsonify
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *

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

  venue_list=[]
  locations = set()
  venues = Venue.query.all()
  for venue in venues:
    locations.add((venue.city, venue.state))
  
  for location in locations:
    venue_list.append({ "city": location[0], "state": location[1], "venues": []})
  
  for venue in venues:
    num_upcoming_shows = 0
    shows = Show.query.filter_by(venue_id=venue.id).all()
    now = datetime.now()
    for show in shows:
      if show.start_time > now:
        num_upcoming_shows += 1
    for location in venue_list:
      if venue.city == location['city'] and venue.state == location['state']:
        location['venues'].append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": num_upcoming_shows
        })

  return render_template('pages/venues.html', areas=venue_list)
  #return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form['search_term']
  results_count = Venue.query.filter(Venue.name.ilike('%'+search_term+'%')).count()
  results = Venue.query.filter(Venue.name.ilike('%'+search_term+'%')).all()
  venues = []
  for result in results:
    shows = Show.query.filter_by(venue_id=result.id).all()
    now = datetime.now()
    upcoming_shows_count = 0
    for show in shows:
      if show.start_time >= now:
        upcoming_shows_count += 1

    venue={
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": upcoming_shows_count
    }
    venues.append(venue)
  response={
    "count": results_count,
    "data": venues
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue_pages = []
  venues = Venue.query.all()
  for venue in venues:
    past_shows = []
    past_shows_count = 0
    upcoming_shows = []
    upcoming_shows_count = 0
    shows = Show.query.filter_by(venue_id=venue.id).all()
    now = datetime.now()
    for show in shows:
      artist = Artist.query.join(Show, Show.artist_id == Artist.id).one()
      #Or use this
      #artist = Artist.query.get(show.artist_id)
      show_detail = {
        "artist_id": show.artist_id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": show.start_time.strftime("%Y-%m-%dT%H:%M:%S")
      }
      if show.start_time >= now:
        upcoming_shows_count += 1
        upcoming_shows.append(show_detail)
      else:
        past_shows_count += 1
        past_shows.append(show_detail)
    venue_page = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    # Need to complete later
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
    }
    venue_pages.append(venue_page)

  venues_list = list(filter(lambda d: d['id'] == venue_id, venue_pages))[0]
  return render_template('pages/show_venue.html', venue=venues_list)

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
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    facebook_link = request.form['facebook_link']
    if request.form['image_link']:
      image_link = request.form['image_link']
    else:
      image_link = "../static/img/default-avatar.jpg"
    if request.form.get('seeking_talent'):
      seeking_talent = True;
    else:
      seeking_talent = False;
    seeking_description = request.form.get('seeking_description')

    venue = Venue(
    name=name, 
    city=city,
    state=state,
    address=address,
    phone=phone,
    genres=genres,
    facebook_link=facebook_link,
    seeking_talent=seeking_talent,
    seeking_description=seeking_description,
    image_link = image_link)

    db.session.add(venue)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()

  if error:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/ 
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    venue = Venue.query.get(venue_id)
    shows = Show.query.filter_by(venue_id=venue_id).all()
    for show in shows:
      db.session.delete(show)
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()

  if error:
    flash('An error occurred. Venue id ' + venue_id + ' could not be delete.')
  else:
    # on successful db insert, flash success
    flash('Venue id' + venue_id + ' was successfully delete!')
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    artist = Artist.query.get(artist_id)
    shows = Show.query.filter_by(artist_id=artist_id).all()
    for show in shows:
      db.session.delete(show)
    db.session.delete(artist)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()

  if error:
    flash('An error occurred. Artist id ' + artist_id + ' could not be delete.')
  else:
    # on successful db insert, flash success
    flash('Artist id' + artist_id + ' was successfully delete!')
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

  return render_template('pages/home.html')
#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  data=[]
  artists = Artist.query.all()
  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name
    })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form['search_term']
  results_count = Artist.query.filter(Artist.name.ilike('%'+search_term+'%')).count()
  results = Artist.query.filter(Artist.name.ilike('%'+search_term+'%')).all()
  artists = []
  for result in results:
    shows = Show.query.filter_by(artist_id=result.id).all()
    now = datetime.now()
    upcoming_shows_count = 0
    for show in shows:
      if show.start_time >= now:
        upcoming_shows_count += 1

    artist={
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": upcoming_shows_count
    }
    artists.append(artist)
  response={
    "count": results_count,
    "data": artists
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist_pages = []
  artists = Artist.query.all()
  for artist in artists:
    past_shows = []
    past_shows_count = 0
    upcoming_shows = []
    upcoming_shows_count = 0
    shows = Show.query.filter_by(artist_id=artist.id).all()
    now = datetime.now()
    for show in shows:
      venue = Venue.query.join(Show, Show.venue_id == Venue.id).one()
      show_detail = {
        "venue_id": show.venue_id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": show.start_time.strftime("%Y-%m-%dT%H:%M:%S")
      }
      if show.start_time >= now:
        upcoming_shows_count += 1
        upcoming_shows.append(show_detail)
      else:
        past_shows_count += 1
        past_shows.append(show_detail)
    artist_page = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    # Need to complete later
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
    }
    artist_pages.append(artist_page)

  artist_list = list(filter(lambda d: d['id'] == artist_id, artist_pages))[0]
  return render_template('pages/show_artist.html', artist=artist_list)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  data=Artist.query.get(artist_id)
  artist={
    "id": data.id,
    "name": data.name,
    "genres": data.genres,
    "city": data.city,
    "state": data.state,
    "phone": data.phone,
    "website": data.website_link,
    "facebook_link": data.facebook_link,
    "seeking_venue": data.seeking_venue,
    "seeking_description": data.seeking_description,
    "image_link": data.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  try:
    artist = Artist.query.get(artist_id)
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form.getlist('genres')  
    artist.facebook_link = request.form['facebook_link']
    if request.form['image_link']:
      artist.image_link = request.form['image_link']
    else:
      artist.image_link = "../static/img/default-avatar.jpg"
    artist.website_link = request.form['website_link']
    if request.form.get('seeking_venue'):
      artist.seeking_venue = True;
    else:
      artist.seeking_venue = False;
    artist.seeking_description = request.form.get('seeking_description')
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()

  if error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
  else:
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully updated!')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  data=Venue.query.get(venue_id)
  venue={
    "id": data.id,
    "name": data.name,
    "genres": data.genres,
    "address": data.address,
    "city": data.city,
    "state": data.state,
    "phone": data.phone,
    "website": data.website_link,
    "facebook_link": data.facebook_link,
    "seeking_talent": data.seeking_talent,
    "seeking_description": data.seeking_description,
    "image_link": data.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False
  try:
    venue = Venue.query.get(venue_id)
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.phone = request.form['phone']
    venue.genres = request.form.getlist('genres')  
    venue.facebook_link = request.form['facebook_link']
    if request.form['image_link']:
      venue.image_link = request.form['image_link']
    else:
      venue.image_link = "../static/img/default-avatar.jpg"
    venue.website_link = request.form['website_link']
    if request.form.get('seeking_venue'):
      venue.seeking_venue = True;
    else:
      venue.seeking_venue = False;
    venue.seeking_description = request.form.get('seeking_description')
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()

  if error:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
  else:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully updated!')

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
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    facebook_link = request.form['facebook_link']
    if request.form['image_link']:
      image_link = request.form['image_link']
    else:
      image_link = "../static/img/default-avatar.jpg"
    website_link = request.form['website_link']
    if request.form.get('seeking_venue'):
      seeking_venue = True;
    else:
      seeking_venue = False;
    seeking_description = request.form.get('seeking_description')

    artist = Artist(
    name=name, 
    city=city,
    state=state,
    phone=phone,
    genres=genres,
    facebook_link=facebook_link,
    seeking_venue=seeking_venue,
    seeking_description=seeking_description,
    image_link = image_link)

    db.session.add(artist)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()

  if error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/ 
  return render_template('pages/home.html')
  # on successful db insert, flash success
  
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  show_lists = []
  shows = Show.query.all()
  for show in shows:
    artist = Artist.query.get(show.artist_id)
    venue = Venue.query.get(show.venue_id)
    show_list = {
      "venue_id": show.venue_id,
      "venue_name": venue.name,
      "artist_id": show.artist_id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_time.strftime("%Y-%m-%dT%H:%M:%S")
    }
    show_lists.append(show_list)
    
  return render_template('pages/shows.html', shows=show_lists)

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
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']

    show = Show(
      artist_id = artist_id,
      venue_id = venue_id,
      start_time = start_time
    )

    db.session.add(show)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()

  if error:
    # TODO: on unsuccessful db insert, flash an error instead.
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/ 
    flash('An error occurred. show ' + request.form['start_time'] + 'with artist id ' + request.form['artist_id'] +' in venue id ' + 
    request.form['venue_id'] + ' could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Show ' + request.form['start_time'] + 'with artist id ' + request.form['artist_id'] +' in venue id ' + 
    request.form['venue_id'] + ' was successfully listed!')

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
