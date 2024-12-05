from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

def create_app():
    app = Flask(__name__)

    # Replace with your actual database URL
    DATABASE_URL = "postgresql+psycopg2://pallet:pallet@localhost/warehouse"

    # Create the SQLAlchemy engine
    engine = create_engine(DATABASE_URL)

    # Create a configured "Session" class
    Session = sessionmaker(bind=engine)

    # Create a Session
    session = Session()

    # Create all tables in the database
    Base.metadata.create_all(engine)

    # Store the session in the app context
    app.session = session

    return app
