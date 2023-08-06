import json
import datetime
import secrets
from sqlalchemy.types import TypeDecorator, VARCHAR
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy import (Column, Integer, Unicode, UnicodeText, DateTime,
    Boolean, ForeignKey, func)
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint
from tcw.database import Base


class JSONEncodedDict(TypeDecorator):
    """
    Store json text as a varchar
    """

    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_variable(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value


class MutableDict(Mutable, dict):
    """
    Convert plain dictionaries to MutableDict
    """

    @classmethod
    def coerce(cls, key, value):
        """
        Coerce to dict
        """

        if not isinstance(value, MutableDict):
            if isinstance(value, dict):
                return MutableDict(value)

            return Mutable.coerce(key, value)
        else:
            return value

    def __setitem__(self, key, value):
        """
        Detect dictionary set events and emit change events.
        """

        dict.__setitem__(self, key, value)
        self.changed()

    def __delitem__(self, key):
        """
        Detect dictionary del events and emit change events.
        """

        dict.__delitem__(self, key)
        self.changed()


class Contest(Base):
    """
    NOTE: Do not use the attributes field for ANYTHING.
    If you do, it will break the sqlalchemy subqueries that check for
    expired contests, and tcw-tasks will break.
    """

    __tablename__ = 'contests'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(48), nullable=False, unique=True)
    title = Column(Unicode(128), nullable=False)
    instructions = Column(UnicodeText, nullable=True)
    email = Column(Unicode(128), nullable=True)
    expires = Column(DateTime, nullable=False, default=func.now())
    winners = Column(Integer, nullable=False, default=1)
    max_entrants = Column(Integer, nullable=False, default=100)
    attributes = Column(MutableDict.as_mutable(JSONEncodedDict), nullable=True)

    # relationships
    entrants = relationship('Entrant', backref='contest', cascade='all,delete')


    def pick_winners(self):
        """
        Pick the winners of the contest.

        args:
            None
        returns:
            list - a list of winning names
        """

        results = []
        nwinners = self.winners
        if len(self.entrants) == 0:
            return []

        if len(self.entrants) < self.winners:
            nwinners = len(self.entrants)

        choices = [e.name for e in self.entrants]
        while len(results) < nwinners:
            name = secrets.choice(choices)
            if name not in results:
                results.append(name)

        return results


class Entrant(Base):
    """
    Entrant class definition
    """

    __tablename__ = 'entrants'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode, nullable=False, unique=False)
    contest_id = Column(Integer, ForeignKey('contests.id'))

    # ensure only one name sign-up per contest.
    __table_args__ = (
        UniqueConstraint('name', 'contest_id', name='_name_id_uc'),)


class Fossil(Base):
    """
    Fossil class definition. This is used only to keep a bare bones crumb
    of info about expired contests
    """

    __tablename__ = 'fossils'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(48), nullable=False, unique=True)
    expired = Column(DateTime, nullable=False, default=func.now())
    attributes = Column(MutableDict.as_mutable(JSONEncodedDict), nullable=True)
