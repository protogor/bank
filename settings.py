from datetime import datetime
from database import db_session
from flask import Flask, session, g, render_template
from bank.models import User


app = Flask(__name__)


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.before_request
def load_current_user():
	pass
    #g.user = User.query.filter_by(openid=session['openid']).first() \
    #    if 'openid' in session else None


@app.teardown_request
def remove_db_session(exception):
    db_session.remove()


@app.context_processor
def date_context():
    return {'current_date_context': datetime.now()}

from bank.views import general

app.register_blueprint(general)


from utils import utils
app.jinja_env.filters['current_date'] = utils.get_current_date
"""
app.jinja_env.filters['dateformat'] = utils.format_date
app.jinja_env.filters['timedeltaformat'] = utils.format_timedelta
app.jinja_env.filters['displayopenid'] = utils.display_openid
"""