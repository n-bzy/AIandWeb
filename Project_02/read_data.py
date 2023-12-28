import csv
from sqlalchemy.exc import IntegrityError
from models import Movie, MovieGenre, MovieLinks, MovieTags, MovieRatings, User
from datetime import datetime


def check_and_read_data(db):
    # check if we have movies in the database
    # read data if database is empty
    if Movie.query.count() == 0:
        # read movies from csv
        with open('data/movies.csv', newline='', encoding='utf8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            count = 0
            for row in reader:
                if count > 0:
                    try:
                        id = row[0]
                        title = row[1]
                        movie = Movie(id=id, title=title)
                        db.session.add(movie)
                        # genres is a list of genres
                        genres = row[2].split('|')
                        # add each genre to the movie_genre table
                        for genre in genres:
                            movie_genre = MovieGenre(movie_id=id, genre=genre)
                            db.session.add(movie_genre)
                        db.session.commit()  # save data to database
                    except IntegrityError:
                        print("Ignoring duplicate movie: " + title)
                        db.session.rollback()
                        pass
                count += 1
                if count % 100 == 0:
                    print(count, " movies read")

        with open('data/links.csv', newline='', encoding='utf8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            count = 0
            for row in reader:
                if count > 0:
                    try:
                        movie_id = row[0]
                        imdb_id = row[1]
                        tmdb_id = row[2]
                        links = MovieLinks(movie_id=movie_id,
                                           imdb_id=imdb_id,
                                           tmdb_id=tmdb_id)
                        db.session.add(links)
                        db.session.commit()
                    except IntegrityError:
                        # print("Ignoring duplicate links: " + movie_id)
                        print("rollback link"+str(count))
                        db.session.rollback()
                        pass
                count += 1
                if count % 100 == 0:
                    print(count, " links read")

        with open('data/tags.csv', newline='', encoding='utf8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            count = 0
            for row in reader:
                if count > 0:
                    try:
                        user_id = row[0]
                        movie_id = row[1]
                        tag = row[2]
                        timestamp = datetime.fromtimestamp(int(row[3]))
                        tags = MovieTags(user_id=user_id,
                                         movie_id=movie_id,
                                         tag=tag,
                                         timestamp=timestamp)
                        db.session.add(tags)
                        db.session.commit()
                    except IntegrityError:
                        print("rollback tag"+str(count))
                        db.session.rollback()
                        pass
                count += 1
                if count % 100 == 0:
                    print(count, " tags read")

        with open('data/ratings.csv', newline='', encoding='utf8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            count = 0
            for row in reader:
                if count > 0:
                    try:
                        user_id = row[0]
                        movie_id = row[1]
                        rating = row[2]
                        timestamp = datetime.fromtimestamp(int(row[3]))
                        ratings = MovieRatings(user_id=user_id,
                                               movie_id=movie_id,
                                               rating=rating,
                                               timestamp=timestamp)
                        db.session.add(ratings)
                        db.session.commit()
                    except IntegrityError:
                        print("rollback rating"+str(count))
                        db.session.rollback()
                        pass
                count += 1
                if count % 100 == 0:
                    print(count, "ratings read")

        with open('data/ratings.csv', newline='', encoding='utf8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            count = 0
            for row in reader:
                if count > 0:
                    try:
                        user_id = row[0]
                        user = User(id=user_id,
                                    active=1,
                                    username="a"+str(count),
                                    password="Qwert"+str(count))
                        db.session.add(user)
                        db.session.commit()
                    except IntegrityError:
                        print("rollback user"+str(count))
                        db.session.rollback()
                        pass
                count += 1
                if count % 100 == 0:
                    print(count, "users read")
