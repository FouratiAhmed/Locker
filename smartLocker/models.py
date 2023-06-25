from datetime import datetime
from smartLocker import db, app, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    address = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file},'{self.address}')"

class User2(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    surname = db.Column(db.String(20), unique=True, nullable=False)
    mail_address = db.Column(db.String(120), unique=True, nullable=False)
    p_p = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    has_moto = db.Column(db.Boolean, default=False)
    has_car = db.Column(db.Boolean, default=False)
    def __repr__(self):
        return f"User('{self.surname}', '{self.mail_address}', '{self.p_p}', '{self.has_moto}', '{self.has_car}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"
with app.app_context():
    db.create_all()