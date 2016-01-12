"""SQLAlchemy base class and used in a declarative way.

When reading the code below, please look through the relevant documentation.
http://flask.pocoo.org/docs/0.10/patterns/sqlalchemy/#declarative
"""

import os

from . import app

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

# TODO(henry): Check if this is environment sensitive.
database_uri = 'sqlite:///' + os.path.join(app.instance_path, 'app.db')
engine = create_engine(database_uri, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import models
    Base.metadata.create_all(bind=engine)

def GetAll(model):
  return model.query.all()

def GetById(model, id):
  return model.query.get(id)

def GetFirstRecord(model):
  return model.query.get(0)

def Add(instance):
  db_session.add(instance)
  db_session.commit()

def Delete(instance):
  db_session.delete(instance)
  db_session.commit()
