import logging
from flask import (Blueprint, render_template, redirect, request, abort,
    url_for)
from sqlalchemy.exc import IntegrityError
from tcw.database import session
from tcw.utils import (contest_by_name, fossil_by_name, random_name,
    expires_time)
from tcw.exc import ContestNotFound, FossilNotFound
from .forms import ContestForm, SignupForm
from .models import Contest, Entrant


logger = logging.getLogger(__name__)
bp = Blueprint('contest', __name__, template_folder='templates')


@bp.route('/', methods=['GET'])
def index():
    """
    Main page
    """

    return render_template('contest/index.html')


@bp.route('/about', methods=['GET'])
def about():
    """
    About page
    """

    return render_template('contest/about.html')


@bp.route('/privacy', methods=['GET'])
def privacy():
    """
    Privacy document
    """

    return render_template('contest/privacy.html')


@bp.route('/contest', methods=['GET', 'POST'])
def new():
    """
    Create a new contest
    """

    form = ContestForm()
    if form.validate_on_submit():
        unique = random_name()
        options = {
            'name': unique,
            'title': form.title.data,
            'instructions': form.instructions.data,
            'email': form.email.data,
            'expires': expires_time(float(form.hours.data)),
            'winners': int(form.winners.data),
            'max_entrants': int(form.maximum.data),
        }

        try:
            obj = Contest(**options)
            session.add(obj)
            session.commit()
            options['expires'] = options['expires'].isoformat() + "Z"
        except:
            abort(404)

        return redirect(url_for('contest.success', **options))

    return render_template('contest/form.html', form=form)


@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    User signup for existing contest
    """

    form = SignupForm()
    try:
        name = request.args.get('name')
    except:
        abort(404)

    try:
        contest = contest_by_name(name)
    except ContestNotFound:
        try:
            fossil = fossil_by_name(name)
        except FossilNotFound:
            abort(404)
        abort(410)

    if form.validate_on_submit():
        if len(contest.entrants) >= contest.max_entrants:
            return render_template('contest/signup.html',
                data=contest, form=form)

        options = {
            'name': form.name.data.split("|")[0],
            'contest_id': contest.id }
        try:
            obj = Entrant(**options)
            session.add(obj)
            session.commit()
            return redirect(
                url_for('contest.thanks',
                    contest=contest.title,
                    entrant=form.name.data), code=303)
        except IntegrityError:
            session.rollback()
            return render_template('contest/sorry.html',
                contest=contest, form=form)
        except:
            abort(404)

    return render_template('contest/signup.html',
        contest=contest, form=form)


@bp.route('/success', methods=['GET'])
def success():
    """
    Contest was successfully created
    """

    return render_template('contest/success.html', data=request.args)


@bp.route('/thanks', methods=['GET'])
def thanks():
    """
    Thanks for signing up!    
    """

    contest = request.args.get('contest')
    entrant = request.args.get('entrant')
    return render_template('contest/thanks.html',
        contest=contest, name=entrant)
