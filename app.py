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
    genre_names = session.query(Genre.genre_name).all()

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
                               order_by(Movie.year_published).all()

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

@app.route("/api/v1.0/profit")
def profit_array():  
    # Query the Heroku Postgres Database to DataFrame for the profit table
    profit_query_stmt = session.query(Profit).statement
    profit_df = pd.read_sql_query(profit_query_stmt, session.bind)

    # Iterate through the profit_tb_df to create a list of dictionaries (array of objects) for each row
    profit_list = []

    for row in profit_df.iterrows():

        # Profit dict
        movie_id = row["movie_id"]
        budget = row["budget"]
        revenue = row["revenue"]
        profit = row["profit"]

        row_profit = {"movie_id": movie_id,
                  "budget": budget,
                  "revenue": revenue,
                  "profit": profit
                 }
        profit_list.append(row_profit)

    return jsonify(profit_list)


# @app.route("/api/v1.0/movies02")
# def profit_movies():  
#     # Query the Heroku Postgres Database to DataFrame and JOIN appropriate tables
#     query1 = session.query(mgjunct.movie_id, Genre.genre_name, Profit.budget, Profit.revenue, Profit.profit,\
#                           Movie.usa_gross_income, Movie.worlwide_gross_income, Movie.movie_title, Movie.year_published,\
#                           Movie.movie_duration, Movie.votes_avg, country.country_name, country.lat,\
#                           country.long, companyname.company_name)
#     query2 = query1.join(Profit, mgjunct.movie_id == Profit.movie_id)
#     query3 = query2.join(Genre, mgjunct.genre_id == Genre.genre_id)
#     query4 = query3.join(Movie, mgjunct.movie_id == Movie.movie_id)
#     query5 = query4.join(countryjunct, Movie.movie_id == countryjunct.movie_id)
#     query6 = query5.join(country, countryjunct.country_id == country.country_id)
#     query_stmt = query6.join(companyname, Movie.company_id == companyname.company_id).statement
#     profit_movies_df = pd.read_sql_query(query_stmt, session.bind)

#     # Iterate through the profit_genre_df to create a list of dictionaries (array of objects) for each row
#     profit_movies_list = []
    
#     for row in profit_movies_df.iterrows():

#         # Profit dict
#         movie_id = row["movie_id"]
#         movie_title = row["movie_title"]
#         year_published = row["year_published"]
#         movie_duration = row["movie_duration"]
#         budget = row["budget"]
#         usa_gross_income = row["usa_gross_income"]
#         worlwide_gross_income = row["worlwide_gross_income"]
#         country_name = row["country_name"]
#         lat = row["lat"]
#         lng = row["long"]
#         votes_avg = row["votes_avg"]
#         genre_name = row["genre_name"]
#         revenue = row["revenue"]
#         profit = row["profit"]
#         country_name = row["country_name"]

#         row_profit_movies = {"movie_id": movie_id,
#                              "title": movie_title,
#                              "year_pub": year_published,
#                              "duration": movie_duration,
#                              "us_gross": usa_gross_income,
#                              "ww_gross": worlwide_gross_income,
#                              "country": country_name,
#                              "lat": lat,
#                              "lng": lng,
#                              "avg_votes": votes_avg,
#                              "company": country_name,
#                             "genre_name": genre_name,
#                             "budget": budget,
#                             "revenue": revenue,
#                             "profit": profit
#                  }
#         profit_movies_list.append(row_profit_movies)
      
#     return jsonify(profit_movies_list)


# @app.route("/api/v1.0/genre02")
# def profit_genre():  
#     # Query the Heroku Postgres Database to DataFrame and JOIN appropriate tables
#     query1 = session.query(mgjunct.movie_id, Genre.genre_name, Profit.budget, Profit.revenue, Profit.profit)
#     query2 = query1.join(Profit, mgjunct.movie_id == Profit.movie_id)
#     query_stmt = query2.join(Genre, mgjunct.genre_id == Genre.genre_id).statement
#     profit_genre_df = pd.read_sql_query(query_stmt, session.bind)
    
#     # Iterate through the profit_genre_df to create a list of dictionaries (array of objects) for each row
#     profit_genre_list = []
    
#     for row in profit_genre_df.iterrows():

#         # Profit dict
#         movie_id = row["movie_id"]
#         genre_name = row["genre_name"]
#         budget = row["budget"]
#         revenue = row["revenue"]
#         profit = row["profit"]

#         row_profit_genre = {"movie_id": movie_id,
#                             "genre_name": genre_name,
#                             "budget": budget,
#                             "revenue": revenue,
#                             "profit": profit
#                  }
#         profit_genre_list.append(row_profit_genre)
      
#     return jsonify(profit_genre_list)

# @app.route("/api/v1.0/companies")
# def movie_company():
#     movie_info = session.query(Movie.movie_title, Movie.year_published,\
#                                Movie.movie_duration, Movie.budget, Movie.usa_gross_income,\
#                                Movie.worlwide_gross_income, companyname.company_name, Movie.votes_avg).filter(\
#                                Movie.company_id == companyname.company_id).\
#                                limit(100).all()

#     session.close()
#     #Create list of movie information
#     movie_list = []
#     for title, year, duration, budget, us, worldwide, company, avg_votes in movie_info:
#         movie_dict = {}
#         movie_dict['title'] = title
#         movie_dict['year_pub'] = year
#         movie_dict['duration'] = duration
#         movie_dict['budget'] = budget
#         movie_dict['us_gross'] = us
#         movie_dict['ww_gross'] = worldwide 
#         movie_dict['company'] = company
#         movie_dict['avg_votes'] = avg_votes
#         movie_list.append(movie_dict)

#     return jsonify(movie_list)

if __name__ == "__main__":   
    app.run(debug=True)