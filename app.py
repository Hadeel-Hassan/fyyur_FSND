#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from datetime import datetime
from flask_migrate import Migrate
from datetime import datetime, date
from forms import *
from forms import VenueForm
import sys
import psycopg2
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

conn = psycopg2.connect("host=localhost dbname=fyyur user=postgres")
cur = conn.cursor()

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    genres = db.Column(db.ARRAY(db.String(50)))
    city = db.Column(db.String(20), db.ForeignKey(
        'venuelocation.city'), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    website = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(200))
    past_shows = db.Column(db.ARRAY(db.String(120)), nullable=True)
    upcoming_shows = db.Column(db.ARRAY(db.String(120)), nullable=True)
    past_shows_count = db.Column(db.Integer, nullable=False, default=0)
    upcoming_shows_count = db.Column(db.Integer, nullable=False, default=0)
    shows = db.relationship('Show', backref='venue', lazy=True)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class VenueLocation(db.Model):
    __tablename__ = 'venuelocation'

    state = db.Column(db.String(2), nullable=False)
    city = db.Column(db.String(20), nullable=False, primary_key=True)
    venues = db.relationship('Venue', backref='location', lazy=True)


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    genres = db.Column(db.ARRAY(db.String(50)), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(500), nullable=True)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    past_shows = db.Column(db.ARRAY(db.String(120)), nullable=True)
    upcoming_shows = db.Column(db.ARRAY(db.String(120)), nullable=True)
    past_shows_count = db.Column(db.Integer, nullable=False, default=0)
    upcoming_shows_count = db.Column(db.Integer, nullable=False, default=0)
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(200))
    shows = db.relationship('Show', backref='artist', lazy=True)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'venue.id'), nullable=False)

#----------------------------------------------------------------------------#
# Initial Data.
#----------------------------------------------------------------------------#
with open('venue_initial_data.csv', 'r') as f:
    next(f)
    cur.copy_from(f, 'venue', sep=',')

conn.commit()

with open('artist_initial_data.csv', 'r') as f:
    next(f)
    cur.copy_from(f, 'artist', sep=',')

conn.commit()

with open('show_initial_data.csv', 'r') as f:
    next(f)
    cur.copy_from(f, 'show', sep=',')

conn.commit()

with open('venuelocation_initial_data.csv', 'r') as f:
    next(f)
    cur.copy_from(f, 'venuelocation', sep=',')

conn.commit()

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
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
    locations = VenueLocation.query.all()
    id_counter = 1
    data = []
    for location in locations:
        venues = Venue.query.filter_by(
            city=location.city).order_by(Venue.id).all()
        venues_array = []
        for venue in venues:
            venues_array.append({
                "id": id_counter,
                "name": venue.name,
            })
            id_counter = id_counter+1
        data.append({
            "city": location.city,
            "state": location.state,
            "venues": venues_array,
        })
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    query = request.form.get('search_term')
    venues_result = Venue.query.filter(Venue.name.ilike(f'%{query}%')).all()
    data = []
    for venue in venues_result:
        data.append({
            "id": venue.id,
            "name": venue.name,
        })
    response = {
        "count": len(venues_result),
        "data": data
    }
    return render_template('pages/search_venues.html', results=response, search_term=str(query))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    venue = Venue.query.filter_by(id=venue_id).first()
    shows = Show.query.filter_by(venue_id=venue_id).all()

    upcoming_shows = []
    past_shows = []
    for show in shows:
        if show.start_time > datetime.now():
            upcoming_shows.append({
                "artist_id": show.artist_id,
                "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
                "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
                "start_time": format_datetime(str(show.start_time))
            })
        elif show.start_time < datetime.now():
            past_shows.append({
                "artist_id": show.artist_id,
                "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
                "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
                "start_time": format_datetime(str(show.start_time))
            })

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": VenueLocation.query.filter_by(city=venue.city).first().state,
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

# @app.route('/venues/create', methods=['POST'])
# def create_venue():


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    form = VenueForm()
    if form.validate_on_submit():
        form = VenueForm()
        if bool(VenueLocation.query.filter_by(city=request.form['city']).first()) == False:
            city = request.form['city']
            state = request.form['state']
            try:
                location = VenueLocation(state=state, city=city)
                db.session.add(location)
                db.session.commit()
            except:
                db.session.rollback()
                flash('Oops! incorrect city/state value. Venue ' +
                      request.form['name'] + ' could not be listed.')
            finally:
                db.session.close()
        try:
            name = request.form['name']
            genres = form.genres.data
            city = request.form['city']
            address = request.form['address']
            phone = request.form['phone']
            image_link = "https://i.ibb.co/31v1Gfq/no-image.png" if form.image_link.data == '' else request.form[
                'image_link']
            website = request.form['website']
            facebook_link = request.form['facebook_link']
            seeking_talent = True if form.seeking_talent.data == 'Yes' else False
            seeking_description = request.form['seeking_description']
            venue = Venue(name=name, genres=genres, city=city,
                          address=address, phone=phone, image_link=image_link,
                          website=website, facebook_link=facebook_link,
                          seeking_talent=seeking_talent, seeking_description=seeking_description)
            db.session.add(venue)
            db.session.commit()
            flash('Venue ' + request.form['name'] +
                  ' was successfully listed!')
        except:
            db.session.rollback()
            flash('Oops! An error ' + str(sys.exc_info()[0]) + ' ocurred. Venue ' +
                  request.form['name'] + ' could not be listed.')
        finally:
            db.session.close()
        return render_template('pages/home.html')
    else:
        return render_template('forms/new_venue.html', form=form)


@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    venue = Venue.query.filter_by(id=venue_id).first()
    name = venue.name
    try:
        db.session.delete(venue)
        db.session.commit()
        all_cities = VenueLocation.query.all()
        for all_city in all_cities:
            venues_city = Venue.query.filter_by(city=all_city.city).first()
            if str(venues_city) == "None":
                city = VenueLocation.query.filter_by(
                    city=all_city.city).first()
                try:
                    db.session.delete(city)
                    db.session.commit()
                except:
                    db.session.rollback()
                    flash('Oops! Venue ' + name +
                          ' could not be deleted. error: ' + str(sys.exc_info()[1]))
                finally:
                    db.session.close()
        flash('Venue ' + name + ' was successfully deleted.')
    except:
        db.session.rollback()
        flash('Oops! Venue ' + name +
              ' could not be deleted. error: ' + str(sys.exc_info()[1]))
    finally:
        db.session.close()

    return redirect(url_for('venues'))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    artists = Artist.query.order_by(Artist.id).all()
    data = []
    for artist in artists:
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
    query = request.form.get('search_term')
    artists_result = Artist.query.filter(Artist.name.ilike(f'%{query}%')).all()
    data = []
    for artist in artists_result:
        data.append({
            "id": artist.id,
            "name": artist.name,
        })
    response = {
        "count": len(artists_result),
        "data": data
    }
    return render_template('pages/search_artists.html', results=response, search_term=str(query))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    artist = Artist.query.filter_by(id=artist_id).first()
    shows = Show.query.filter_by(artist_id=artist_id).all()

    upcoming_shows = []
    past_shows = []
    for show in shows:
        if show.start_time > datetime.now():
            upcoming_shows.append({
                "venue_id": show.venue_id,
                "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
                "venue_image_link": Venue.query.filter_by(id=show.venue_id).first().image_link,
                "start_time": format_datetime(str(show.start_time))
            })
        elif show.start_time < datetime.now():
            past_shows.append({
                "venue_id": show.venue_id,
                "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
                "venue_image_link": Venue.query.filter_by(id=show.venue_id).first().image_link,
                "start_time": format_datetime(str(show.start_time))
            })
    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
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
    form = EditArtistForm()
    _artist = Artist.query.filter_by(id=artist_id).first()
    artist = {
        "id": _artist.id,
        "name": _artist.name,
        "genres": _artist.genres,
        "city": _artist.city,
        "phone": _artist.phone,
        "website": _artist.website,
        "facebook_link": _artist.facebook_link,
        "seeking_description": _artist.seeking_description if _artist.seeking_description != '' else "Description For Venue...",
        "image_link": _artist.image_link,
    }
    form.state.default = _artist.state
    form.seeking_venue.default = "Yes" if _artist.seeking_venue == True else "No"
    form.process()
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    form = EditArtistForm()
    _artist = Artist.query.filter_by(id=artist_id).first()
    if form.validate_on_submit():
        try:
            _artist.name = _artist.name if request.form['name'] == '' else request.form['name']
            _artist.genres = form.genres.data if form.genres.data != [] else _artist.genres
            _artist.city = _artist.city if request.form['city'] == '' else request.form['city']
            _artist.state = _artist.state if request.form['state'] == _artist.state else request.form['state']
            _artist.phone = _artist.phone if request.form['phone'] == '' else request.form['phone']
            _artist.image_link = _artist.image_link if form.image_link.data == '' else request.form[
                'image_link']
            _artist.website = _artist.website if request.form[
                'website'] == '' else request.form['website']
            _artist.facebook_link = _artist.facebook_link if request.form[
                'facebook_link'] == '' else request.form['facebook_link']
            _artist.seeking_venue = True if form.seeking_venue.data == 'Yes' else False
            _artist.seeking_description = _artist.seeking_description if request.form[
                'seeking_description'] == '' else request.form['seeking_description']
            db.session.commit()
            flash('Artist ' + request.form['name'] +
                  ' was successfully edited!')
        except:
            db.session.rollback()
            flash('Oops! An error ocurred. Artist ' +
                  request.form['name'] + ' could not be edited. error: ' + str(sys.exc_info()[1]))
        finally:
            db.session.close()
        return redirect(url_for('show_artist', artist_id=artist_id))
    else:
        artist = {
            "id": artist_id,
            "name": _artist.name if request.form['name'] == '' else request.form['name'],
            "genres": form.genres.data if form.genres.data != [] else _artist.genres,
            "city": _artist.city if request.form['city'] == '' else request.form['city'],
            "phone": _artist.phone if request.form['phone'] == '' else request.form['phone'],
            "image_link": _artist.image_link if form.image_link.data == '' else request.form['image_link'],
            "website": _artist.website if request.form['website'] == '' else request.form['website'],
            "facebook_link": _artist.facebook_link if request.form['facebook_link'] == '' else request.form['facebook_link'],
            "seeking_venue": True if form.seeking_venue.data == 'Yes' else False,
            "seeking_description": _artist.seeking_description if request.form['seeking_description'] == '' else request.form['seeking_description'],
        }
        form.state.default = _artist.state
        return render_template('forms/edit_venue.html', form=form, artist=artist)


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = EditVenueForm()
    _venue = Venue.query.filter_by(id=venue_id).first()
    state = VenueLocation.query.filter_by(city=_venue.city).first().state
    form.state.default = state
    form.process()
    venue = {
        "id": _venue.id,
        "name": _venue.name,
        "genres": _venue.genres,
        "address": _venue.address,
        "city": _venue.city,
        "phone": _venue.phone,
        "website": _venue.website,
        "facebook_link": _venue.facebook_link,
        "seeking_description": _venue.seeking_description if _venue.seeking_description != '' else "Description For Talent...",
        "image_link": _venue.image_link,
    }
    form.seeking_talent.default = "Yes" if _venue.seeking_talent == True else "No"
    form.process()
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    form = EditVenueForm()
    _venue = Venue.query.filter_by(id=venue_id).first()
    location = VenueLocation.query.filter_by(city=_venue.city).first()
    if form.validate_on_submit():
        try:
            _venue.name = _venue.name if request.form['name'] == '' else request.form['name']
            _venue.genres = form.genres.data if form.genres.data != [] else _venue.genres
            _venue.city = _venue.city if request.form['city'] == '' else request.form['city']
            location.state = location.state if request.form[
                'state'] == location.state else request.form['state']
            _venue.address = _venue.address if request.form['address'] == '' else request.form['address']
            _venue.phone = _venue.phone if request.form['phone'] == '' else request.form['phone']
            _venue.image_link = _venue.image_link if form.image_link.data == '' else request.form[
                'image_link']
            _venue.website = _venue.website if request.form['website'] == '' else request.form['website']
            _venue.facebook_link = _venue.facebook_link if request.form[
                'facebook_link'] == '' else request.form['facebook_link']
            _venue.seeking_talent = True if form.seeking_talent.data == 'Yes' else False
            _venue.seeking_description = _venue.seeking_description if request.form[
                'seeking_description'] == '' else request.form['seeking_description']

            venues_cities = Venue.query(Venue.city).all()
            all_cities = VenueLocation.qurey(VenueLocation.city).all()
            for all_city in all_cities:
                venues_city = Venue.query.filter_by(city=all_city).first()
                if venues_city == []:
                    city = VenueLocation.query.filter_by(city=all_city).first()
                    db.session.delete(city)
                    db.session.commit()
            db.session.commit()
            flash('Venue ' + request.form['name'] +
                  ' was successfully edited!')
        except:
            db.session.rollback()
            flash('Oops! An error ocurred. Venue ' +
                  request.form['name'] + ' could not be edited.')
        finally:
            db.session.close()
        return redirect(url_for('show_venue', venue_id=venue_id))
    else:
        venue = {
            "id": venue_id,
            "name": _venue.name if request.form['name'] == '' else request.form['name'],
            "genres": form.genres.data if form.genres.data != [] else _venue.genres,
            "city": _venue.city if request.form['city'] == '' else request.form['city'],
            "address": _venue.address if request.form['address'] == '' else request.form['address'],
            "phone": _venue.phone if request.form['phone'] == '' else request.form['phone'],
            "image_link": _venue.image_link if form.image_link.data == '' else request.form['image_link'],
            "website": _venue.website if request.form['website'] == '' else request.form['website'],
            "facebook_link": _venue.facebook_link if request.form['facebook_link'] == '' else request.form['facebook_link'],
            "seeking_talent": True if form.seeking_talent.data == 'Yes' else False,
            "seeking_description": _venue.seeking_description if request.form['seeking_description'] == '' else request.form['seeking_description'],
        }
        return render_template('forms/edit_venue.html', form=form, venue=venue)

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
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    form = ArtistForm()
    if form.validate_on_submit():
        try:
            name = request.form['name']
            genres = form.genres.data
            city = request.form['city']
            state = request.form['state']
            phone = request.form['phone']
            image_link = "https://i.ibb.co/31v1Gfq/no-image.png" if form.image_link.data == '' else request.form[
                'image_link']
            website = request.form['website']
            facebook_link = request.form['facebook_link']
            seeking_venue = True if form.seeking_venue.data == 'Yes' else False
            seeking_description = request.form['seeking_description']
            artist = Artist(name=name, genres=genres, city=city,
                            state=state, phone=phone, image_link=image_link,
                            website=website, facebook_link=facebook_link,
                            seeking_venue=seeking_venue, seeking_description=seeking_description)
            db.session.add(artist)
            db.session.commit()
            flash('Artist ' + request.form['name'] +
                  ' was successfully listed!')
        except:
            db.session.rollback()
            flash('Oops! An error ' + str(sys.exc_info()[1]) + ' ocurred. Artist ' +
                  request.form['name'] + ' could not be listed.')
        finally:
            db.session.close()
        return render_template('pages/home.html')
    else:
        return render_template('forms/new_artist.html', form=form)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    all_data = db.session.query(Show.venue_id, Venue.name, Show.artist_id, Artist.name, Artist.image_link, Show.start_time).join(
        Artist).join(Venue).filter(Show.artist_id == Artist.id, Show.venue_id == Venue.id).all()
    data = []
    for d in all_data:
        data.append({
            "venue_id": d[0],
            "venue_name": d[1],
            "artist_id": d[2],
            "artist_name": d[3],
            "artist_image_link": d[4],
            "start_time": format_datetime(str(d[5])),
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

    # on successful db insert, flash success
    
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    form = ShowForm()
    if form.validate_on_submit():
        try:
            artist = Artist.query.filter_by(id=request.form['artist_id']).first()
            venue = Venue.query.filter_by(id=request.form['venue_id']).first()
            show = Show(artist=artist, venue=venue, start_time=request.form['start_time'])
            db.session.add(show)
            db.session.commit()
            flash('Show was successfully listed!')
        except:
            db.session.rollback()
            flash('Oops! The error: ' + str(sys.exc_info()[1]) + ' ocurred. Show could not be listed.')
        finally:
            db.session.close()
        return render_template('pages/home.html')
    return render_template('forms/new_show.html', form=form)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
