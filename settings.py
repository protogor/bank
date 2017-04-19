from datetime import datetime
from database import db_session
from flask import Flask, session, g, render_template

from utils import utils
from bank.views import general


app = Flask(__name__)

# handler error 404
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

# middleware
@app.teardown_request
def remove_db_session(exception):
    db_session.remove()


@app.before_request
def load_current_user():
	pass

# context processor
@app.context_processor
def date_context():
    return {'current_date_context': datetime.now()}


# blueprint
app.register_blueprint(general)

# filter jinja
app.jinja_env.filters['current_date'] = utils.get_current_date
