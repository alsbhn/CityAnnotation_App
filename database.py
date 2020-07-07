import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("sqlite:////database.db") # database engine object from SQLAlchemy that manages connections to the database
                                                    # DATABASE_URL is an environment variable that indicates where the database lives
db = scoped_session(sessionmaker(bind=engine))    # create a 'scoped session' that ensures different users' interactions with the

#f = open("googlenews_top_monthly_2019_45cities_text_6.csv")
#reader = csv.reader(f)
#for ID, city, month, url, text, title, summary, keywords in reader: # loop gives each column a name
      db.execute("INSERT INTO googlenews (ID, city, month, url, text, title, summaty, keywords) VALUES (:ID, :city, :month, :url, :text, :title, :summaty, :keywords)",
                  {"ID": ID, "city": city, "month": month, "url": url, "text": text, "title": title, "summary": summary, "keywords": keywords}) # substitute values from CSV line into SQL command, as per this dict
      print(f"Added news about {city} in month {month}.")
db.commit() # transactions are assumed, so close the transaction finished

db.execute("INSERT INTO newtable (name, id) VALUES (:name, :id)",
                  {"name": 'ali2', "id": 26})
db.commit()                                                    # database are kept separate

#db.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")
#db.commit()

#flights = db.execute("SELECT origin, destination, duration FROM flights").fetchall() # execute this SQL command and return all of the results
#for flight in flights:
#    print(f"{flight.origin} to {flight.destination}, {flight.duration} minutes.") # for every flight, print out the flight info



  