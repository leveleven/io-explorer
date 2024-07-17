from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///io-explorer.db', pool_size=1024, max_overflow=65536)
db_session = scoped_session(sessionmaker(autoflush=False,
                                         autocommit=False, 
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    import models
    Base.metadata.create_all(bind=engine)