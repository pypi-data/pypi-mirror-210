import string
import secrets
import datetime
import markdown
from tcw.apps.contest.models import Contest, Fossil
from .database import session
from .exc import ContestNotFound, FossilNotFound


def contest_by_name(name):
    """
    Get contest object by name
    """

    contest = session.query(Contest).filter(Contest.name == name).one()
    if not contest:
        raise ContestNotFound(f"No contest with name {name}")

    return contest


def fossil_by_name(name):
    """
    Get fossil object by name
    """

    fossil = session.query(Fossil).filter(Fossil.name == name).one()
    if not fossil:
        raise FossilNotFound(f"No fossil with name {name}")

    return fossil


def random_name(length=24):
    """
    create random name for contests. a mix of alphanum chars.

    args:
        - int name length
    returns:
        - str
    """

    letters = string.ascii_letters
    digits = string.digits
    alphabet = letters + digits
    name = ''

    while len(name) < length:
        name += secrets.choice(alphabet)

    return name


def expires_time(hours=1):
    """
    get a datetime object x number of hours in the future.

    args:
        - float hours into the future
    returns:
        - datateime object, None on  error
    """

    now = datetime.datetime.utcnow().replace(second=0, microsecond=0)
    later = now + datetime.timedelta(hours=hours)

    return later


def md_to_html(txt):
    """
    Convert markdown text to HTML.

    args:
        - str (markdown text)
    returns:
        str (html text)
    """

    html = markdown.markdown(txt)
    return html
