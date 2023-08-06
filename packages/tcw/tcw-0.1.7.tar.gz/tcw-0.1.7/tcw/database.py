from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, create_session
from sqlalchemy.ext.declarative import declarative_base

# globals #
engine = None
session = scoped_session(lambda: create_session( bind=engine,
                                                    autocommit=False,
                                                    autoflush=False ))

Base = declarative_base()
Base.query = session.query_property()


def init_db(uri, echo=False):
    """
    Initialize the database.

    args:
        - db uri
        - sqlalchemy echo?
    """

    init_engine(uri, echo=echo)
    init_tables()


def init_engine(uri, **kwargs):
    """
    initialize the global engine for sessions.

    args:
        - db uri
        - keyword args (see sqlalchemy create_engine() docs)
    """

    global engine
    engine = create_engine(uri, **kwargs)


def init_tables():
    """
    Initialize database tables for app models.
    """
    from tcw.apps.contest.models import Contest, Fossil, Entrant
    Base.metadata.create_all(bind=engine)
