from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from datetime import timedelta



app = Flask(__name__)

app.config['SECRET_KEY']='0eddfc389cb552bdb12c7eee655d0d82'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///site.db'
app.config['REMEMBER_COOKIE_DURATION']=timedelta(seconds=20)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from smartLocker import routes