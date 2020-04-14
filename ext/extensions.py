from config import Config

from flask import Flask, render_template, request, redirect, url_for, session, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# app = Flask(__name__)
# app.config.from_object(Config)
db = SQLAlchemy()
migrate = Migrate()