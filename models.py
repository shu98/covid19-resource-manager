from app import db
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

resource_categories = db.Table('resource_categories', 
    db.Column('resource_id', db.Integer, db.ForeignKey('resources.id')),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id'))
)

same_as = lambda col: lambda ctx: ctx.current_parameters.get(col)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_admin = db.Column(db.Boolean(), default=False)

    email = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'), nullable=True)
    resource = db.relationship('Resource')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.email)

class Resource(db.Model):
    __tablename__ = 'resources'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text(), index=True, unique=True, nullable=False)
    institution = db.Column(db.String(255), index=True)
    description = db.Column(db.Text(), index=True, default='')
    link = db.Column(db.Text(), index=True, unique=True, nullable=False)
    submitter = db.Column(db.String(255), index=True)
    date_added = db.Column(db.DateTime(), index=True, default=datetime.utcnow)
    file_location = db.Column(db.Text(), default='')
    iped_ad = db.Column(db.Text(), index=True)
    resource_type = db.Column(db.String(255), index=True)

    upvotes = db.relationship(User, backref='resources', lazy='dynamic')
    show = db.Column(db.Boolean(), default=False)

    categories = db.relationship('Category', secondary=resource_categories, lazy='dynamic')

    def __repr__(self):
        return '<Resource title:{}, source:{}, link:{}, categories{}>'.format(self.title[:20], self.institution, self.link, self.categories)

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), index=True, nullable=False, unique=True)
    slug = db.Column(db.String(255), index=True, nullable=False, default=same_as('name'))
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)

    resources = db.relationship('Resource', secondary=resource_categories, lazy='dynamic')

    def __repr__(self):
        return "<{}:{}>".format(self.id, self.name)