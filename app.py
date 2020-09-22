import pandas as pd
# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify, render_template

#################################################
# Database Setup
#################################################
# rds_connection_string = f'postgres:postgres@localhost:5432/movies_db'
# engine = create_engine(f'postgresql://{rds_connection_string}')
url = 'postgres://kkmcxxxwavsdqd:fb334108f7a36d00866d3a010c69877e6821be0b66fb54f99a642229daaa570a@ec2-54-211-169-227.compute-1.amazonaws.com:5432/d7hg3bbhtgeuu2'
engine = sqlalchemy.create_engine(url)
# Initialize the Base object using the automap_base in order to refelect the database.
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

print(Base.classes.keys())

# Save reference to the table
Movie = Base.classes.movie
Genre = Base.classes.genre
mgjunct = Base.classes.movie_genre_junction
country = Base.classes.country_origin
countryjunct = Base.classes.movie_country_junction
companyname = Base.classes.production_company
Profit = Base.classes.profit
Poster = Base.classes.poster


# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return render_template('index.html')
        
@app.route("/api/v1.0")
def show_apis():
    """List all available api routes."""
    return (
        f"<h4>Available Routes:</h4>"
        f'<a href="/api/v1.0/movies">/api/v1.0/movies</a><br/>'    
        f'<a href="/api/v1.0/genre_names">/api/v1.0/genre_names</a><br/>' 
        f'<a href="/api/v1.0/genre_map">/api/v1.0/genre_map</a><br/>' 
        f'<a href="/api/v1.0/genre_charts">/api/v1.0/genre_charts</a><br/>'
        f'<a href="/api/v1.0/posters">/api/v1.0/posters</a><br/>'
        f'<a href="/api/v1.0/profit_movies">/api/v1.0/profit_movies</a><br/>'
        f'<a href="/"><h4>Back</h4></a><br/>' 
    )   

@app.route("/api/v1.0/movies")
def movie_info():
    movie_info = session.query(Movie.movie_id, Movie.movie_title, Movie.year_published,\
                               country.country_name, country.lat, country.long,\
                               companyname.company_name).filter(\
                               Movie.movie_id == countryjunct.movie_id).filter(\
                               Movie.company_id == companyname.company_id).filter(\
                               countryjunct.country_id == country.country_id).\
                               all()

    session.close()
    #Create list of movie information
    movie_list = []
    for movie_id, title, year, country_name, lat, lng, company in movie_info:
        movie_dict = {}
        movie_dict['movie_id'] = movie_id
        movie_dict['title'] = title
        movie_dict['year_pub'] = year 
        movie_dict['country'] = country_name
        movie_dict['lat'] = lat
        movie_dict['lng'] = lng
        movie_dict['company'] = company
        movie_list.append(movie_dict)

    return jsonify(movie_list)

@app.route("/api/v1.0/genre_names")
def genre_names():
    genre_names = session.query(Genre.genre_name).filter(\
                               Genre.genre_name.isnot(None)).all()

    session.close()
    #Create list of movie information
    genre_names_list = []
    for genre in genre_names:
        genre_names_dict = {}
        genre_names_dict['genre'] = genre
        genre_names_list.append(genre_names_dict)

    return jsonify(genre_names_list)

@app.route("/api/v1.0/genre_map")
def genre_map_info():
    genre_map_info = session.query(Movie.movie_id, Movie.movie_title, Movie.year_published,\
                               country.country_name, country.lat, country.long,\
                               Genre.genre_name,\
                               companyname.company_name).filter(\
                               Movie.movie_id == countryjunct.movie_id).filter(\
                               Movie.company_id == companyname.company_id).filter(\
                               Movie.movie_id == mgjunct.movie_id).filter(\
                               mgjunct.genre_id == Genre.genre_id).filter(\
                               countryjunct.country_id == country.country_id).all()

    session.close()
    #Create list of movie information
    genre_map_list = []
    for movie_id, title, year, country_name, lat, lng, genre, company in genre_map_info:
        genre_map_dict = {}
        genre_map_dict['movie_id'] = movie_id
        genre_map_dict['title'] = title
        genre_map_dict['year_pub'] = year
        genre_map_dict['country'] = country_name
        genre_map_dict['lat'] = lat
        genre_map_dict['lng'] = lng
        genre_map_dict['genre'] = genre
        genre_map_dict['company'] = company
        genre_map_list.append(genre_map_dict)

    return jsonify(genre_map_list)

@app.route("/api/v1.0/genre_charts")
def genre_chart_info():
    genre_chart_info = session.query(Movie.movie_title,\
                               Movie.year_published,\
                               Movie.worlwide_gross_income,\
                               Genre.genre_name).filter(\
                               Movie.movie_id == mgjunct.movie_id).filter(\
                               mgjunct.genre_id == Genre.genre_id).\
                               order_by(Movie.year_published).filter(\
                               Movie.worlwide_gross_income.isnot(None)).all()

    session.close()
    #Create list of movie information
    genre_chart_list = []
    for title, year, worldwide, genre in genre_chart_info:
        genre_chart_dict = {}
        genre_chart_dict['title'] = title
        genre_chart_dict['year_pub'] = year
        genre_chart_dict['ww_gross'] = worldwide 
        genre_chart_dict['genre'] = genre
        genre_chart_list.append(genre_chart_dict)

    return jsonify(genre_chart_list)

@app.route("/api/v1.0/posters")
def poster():
    # Query the Heroku Postgres Database for poster url
    poster_query_stmt = session.query(Poster).statement
    poster_df = pd.read_sql_query(poster_query_stmt, session.bind)
    
    # Iterate through the poster_df to create a list of dictionaries (array of objects) for each row
    poster_list = []
    
    for index, row in poster_df.iterrows(): 
        # Poster dict
        movie_id = row["movie_id"]
        poster_url = row["poster_url"]

        row_profit = {
            "movie_id": movie_id,
            "poster_url": poster_url,

        }
        poster_list.append(row_profit)
      
    return jsonify(poster_list)

@app.route("/api/v1.0/profit_movies")
def profit_route():  
    # Query the Heroku Postgres Database to DataFrame and JOIN appropriate tables
    profit_query_1 = session.query(Profit.movie_id, Profit.budget, Profit.revenue, Profit.profit, Movie.movie_title,\
                          Movie.year_published, Movie.description, Movie.movie_duration, Poster.poster_url)
    profit_query_2 = profit_query_1.join(Movie, Profit.movie_id == Movie.movie_id)
    profit_query_stmt = profit_query_2.join(Poster, Profit.movie_id == Poster.movie_id).statement
    profit_movies_df = pd.read_sql_query(profit_query_stmt, session.bind)

    # Iterate through the profit_movies_df to create a list of dictionaries (array of objects) for each row
    profit_movies_list = []
    
    for index, row in profit_movies_df.iterrows():

        # Profit dict
        movie_id = row["movie_id"]
        movie_title = row["movie_title"]
        year_published = row["year_published"]
        movie_duration = row["movie_duration"]
        description = row["description"]
        budget = row["budget"]
        revenue = row["revenue"]
        profit = row["profit"]
        poster_url = row["poster_url"]

        row_profit_movies = {"movie_id": movie_id,
                            "title": movie_title,
                            "year_pub": year_published,
                            "duration": movie_duration,
                            "description": description,
                            "budget": budget,
                            "revenue": revenue,
                            "profit": profit,
                            "poster_url": poster_url
                 }
        profit_movies_list.append(row_profit_movies)
      
    return jsonify(profit_movies_list)

if __name__ == "__main__":   
    app.run(debug=True)