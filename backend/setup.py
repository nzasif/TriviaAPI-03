from flask import Flask
from flask_sqlalchemy import SQLAlchemy

#----------------------------------------------------------------------------#
# App and db Setup.
#----------------------------------------------------------------------------#
database_path = 'postgresql://asif:1@localhost:5432/triviaDb' 
db = SQLAlchemy()

def setup_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()

app = Flask(__name__)
setup_db(app)




