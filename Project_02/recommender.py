# Contains parts from:
# https://flask-user.readthedocs.io/en/latest/quickstart_app.html

from flask import Flask, render_template, request, redirect, url_for
from flask_user import login_required, UserManager, current_user
from models import db, User, Movie, MovieRatings, MovieGenre
from read_data import check_and_read_data
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from sqlalchemy.exc import IntegrityError


# Class-based application configuration
class ConfigClass(object):
    """ Flask application config """

    # Flask settings
    SECRET_KEY = 'This is an INSECURE secret!! DO NOT use this in production!!'

    # Flask-SQLAlchemy settings
    # File-based SQL database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///movie_recommender.sqlite'
    # Avoids SQLAlchemy warning
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-User settings
    # Shown in and email templates and page footers
    USER_APP_NAME = "Movie Recommender"
    USER_ENABLE_EMAIL = False  # Disable email authentication
    USER_ENABLE_USERNAME = True  # Enable username authentication
    USER_REQUIRE_RETYPE_PASSWORD = True  # Simplify register form

    USER_AFTER_LOGIN_ENDPOINT = 'home_page'
    USER_AFTER_LOGOUT_ENDPOINT = 'home_page'
    USER_AFTER_REGISTER_ENDPOINT = 'home_page'
    USER_AFTER_REGISTER_ENDPOINT = 'home_page'
    USER_AFTER_CONFIRM_ENDPOINT = 'home_page'
    USER_AFTER_LOGIN_ENDPOINT = 'home_page'
    USER_AFTER_LOGOUT_ENDPOINT = 'home_page'


# Create Flask app
app = Flask(__name__)
app.config.from_object(__name__ + '.ConfigClass')  # configuration
app.app_context().push()  # create an app context before initializing db
db.init_app(app)  # initialize database
db.create_all()  # create database if necessary
user_manager = UserManager(app, db, User)  # initialize Flask-User management


@app.cli.command('initdb')
def initdb_command():
    global db
    """Creates the database tables."""
    check_and_read_data(db)
    print('Initialized the database.')


# The Home page is accessible to anyone
@app.route('/')
def home_page():
    # render home.html template
    return render_template("home.html")


# The Members page is only accessible to authenticated users
# via the @login_required decorator
@app.route('/movies', methods=['GET', 'POST'])
@login_required  # User must be authenticated
def movies_page():
    # String-based templates

    genres = ["Action", "Adventure", "Animation", "Children's", "Comedy", "Crime",
              "Documentary", "Drama", "Fantasy", "Film-Noir", "Horror", "Musical",
              "Mystery", "Romance", "Sci-Fi", "Thriller", "War", "Western"]

    selected_entries = request.form.getlist('selectedEntries')

    movies = recommend(selected_entries)
    dic = {}
    for m in movies:
        rating_li = []
        for r in m.ratings:
            rating_li.append(r.rating)
        if rating_li:
            dic[m] = (round(np.mean(rating_li), 1),
                      "based on "+str(len(rating_li))+" reviews")
        else:
            dic[m] = ("No rating yet", "")

    return render_template("movies.html", movies=dic.keys(), genres=genres,
                           ratings=dic, selected_entries=selected_entries)


@app.route('/rate', methods=['POST'])
@login_required  # User must be authenticated
def rate():
    movieid = request.form.get('movieid')
    rating = request.form.get('rating')
    userid = current_user.id
    # print("Rate {} for {} by {}".format(rating, movieid, userid))
    try:
        ratings = MovieRatings(user_id=userid,
                               movie_id=movieid,
                               rating=rating)
        db.session.add(ratings)
        db.session.commit()
    except IntegrityError:
        # print("rollback rating")
        db.session.rollback()
        pass
    return render_template("rated.html", rating=rating)


# Recommender system:
def recommend(genres, rec_no=15):
    userid = current_user.id
    rate = MovieRatings.query.filter_by(user_id=userid).all()
    # If user has ratings already, use recommender
    if rate:
        movies = find_k_nearest_neighbors(userid)
        m_ids = [m.movie_id for m in movies]
        movies = [Movie.query.get(m_id) for m_id in m_ids]
        # If genres are selected, only show movies with these genres
        if genres:
            movies = [movie for movie in movies
                      if any(genre in [g.genre for g in movie.genres]
                             for genre in genres)
                      and not any(rating.user_id == userid for rating in movie.ratings)
                      ]
        else:
            movies = [movie for movie in movies
                      if not any(rating.user_id == userid for rating in movie.ratings)
                      ]

    # If the user does not have ratings yet, recommend movies based on genre
    else:
        movies = Movie.query\
            .filter(Movie.genres.any(MovieGenre.genre.in_(genres))).all()

    return movies[:rec_no]


def find_k_nearest_neighbors(user_id, k=5):
    # Query for the ratings of the target user
    target_user_ratings = MovieRatings.query.filter_by(user_id=user_id).all()

    # Query for all users' ratings excluding the target user
    all_users_ratings = MovieRatings.query.filter(MovieRatings.user_id != user_id).all()

    # Create dictionaries to store movie ratings for calculations
    target_user_dict = {rating.movie_id:
                        rating.rating for rating in target_user_ratings}
    all_users_dict = {rating.user_id:
                      {rating.movie_id: rating.rating} for rating in all_users_ratings}

    # Calculate cosine similarity between the target user and all other users
    similarities = {}
    for other_user_id, other_user_ratings in all_users_dict.items():
        target_vector = np.array([target_user_dict.get(movie_id, 0)
                                  for movie_id in other_user_ratings.keys()])
        other_vector = np.array(list(other_user_ratings.values()))

        cosine_sim = cosine_similarity([target_vector], [other_vector])[0][0]
        similarities[other_user_id] = cosine_sim

    # Sort users by similarity in descending order
    sorted_neighbors = sorted(similarities.items(), key=lambda x: x[1], reverse=True)

    # Get the top k neighbors
    top_k_neighbors = sorted_neighbors[:k]
    # print(top_k_neighbors)

    # Retrieve movie ratings for the top k neighbors
    neighbors_ratings = []
    for neighbor_id, _ in top_k_neighbors:
        neighbor_ratings = MovieRatings.query.filter_by(user_id=neighbor_id).all()
        neighbors_ratings.extend(neighbor_ratings)

    # Sort the results by rating in descending order
    sorted_results = sorted(neighbors_ratings, key=lambda x: x.rating, reverse=True)

    return sorted_results


# TODO
@app.route('/rated_movies', methods=['GET', 'POST'])
@login_required  # User must be authenticated
def rated_movies():
    # list all rated movies by the current user
    userid = current_user.id
    r_list = MovieRatings.query.filter_by(user_id=userid).all()
    m_ids = [(m.movie_id, m) for m in r_list]
    r_list = [(Movie.query.get(m_id[0]), m_id[1]) for m_id in m_ids]

    delete_message = request.args.get('delete_message', '')
    return render_template("rated_movies.html",
                           r_list=r_list,
                           delete_message=delete_message)


@app.route('/delete_entry/<int:entry_id>', methods=['POST'])
def delete_entry(entry_id):
    # Delete Movies from the rating database of the current user
    entry = MovieRatings.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    delete_message = Movie.query.get(entry.movie_id).title
    return redirect(url_for('rated_movies', delete_message=delete_message))


# Start development web server
if __name__ == '__main__':
    app.run(port=5000, debug=True)
