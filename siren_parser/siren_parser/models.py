from sqlalchemy import create_engine, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from siren_parser import settings

metadata = MetaData()
Base = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(URL(**settings.DATABASE))


class Video(Base):

    __tablename__ = 'video'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    name = Column('name', String)
    year_of_issue = Column('year_of_issue', String, nullable=True)
    country = Column('country', String)
    genre = Column('genre', String)
    duration = Column('duration', Integer)
    premiere = Column('premiere', String, nullable=True)
    description = Column('description', String, nullable=True)
    photo = Column('photo', String)
    type = Column('type', Integer, nullable=True)
    season = Column('season', Integer, nullable=True)
    last_episode = Column('last_episode', String, nullable=True)
    label = Column('label', String, nullable=True)


class Website(Base):

    __tablename__ = 'website'

    id = Column('id', Integer, primary_key=True)
    title = Column('title', String, default='kinogo.club')
    quality = Column('quality', String)
    translation = Column('translation', String)
    update_date = Column('update_date', String)
    link_to_watch_online = Column('link_to_watch_online', String, nullable=True)
    video_id = Column('video_id', Integer, ForeignKey('video.id'), nullable=False)
    video = relationship("Video", primaryjoin='Website.video_id==Video.id', uselist=True,
                           backref="video")


def create_tables(engine):
    """"""
    Base.metadata.create_all(engine)
