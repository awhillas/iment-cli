import os
import sys

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

class Image(Base):
    __tablename__ = 'image'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)

class Location(Base):
    __tablename__ = 'location'

    filepath = Column(String(255), primary_key=True)
    # Fingerprint here is just for reverse exact lookup, similarity is done using a BK Tree.
    fingerprint = Column(String, nullable=False)  # A String coz SQLite can't handle BigInteger :(
    image_id = Column(Integer, ForeignKey('image.id'))
    image = relationship(Image, backref='files')
    location_type = Column(String(10), nullable=False, default='local')  # add s3, dropbox, flickr etc
    file_format = Column(String(10), nullable=False)
    width = Column(Integer)
    height = Column(Integer)
    created_on = Column(DateTime)
    added_on = Column(DateTime, default=func.now())

def create_album(connection_uri:str):
    # Create an engine that stores data in A *.db file.
    engine = create_engine(connection_uri)
    # Create all tables in the engine. This is equivalent to "Create Table"
    # statements in raw SQL.
    Base.metadata.create_all(engine)

def open_album(connection_uri:str):
    """ open an album (Db session) """
    engine = create_engine(connection_uri)
    # Bind the engine to the metadata of the Base class so that the
    # declaratives can be accessed through a DBSession instance
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    return DBSession()
