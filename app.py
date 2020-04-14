import os
import sys
import json
from datetime import datetime
from config import Config

from flask import Flask, render_template, Response, request, redirect, url_for, session, make_response
from flask_login import LoginManager
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import urllib.parse

app = Flask(__name__)
app.config.from_object(Config)

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(app, metadata=metadata)
migrate = Migrate(app, db, render_as_batch=True)

from db_functions import *
from models import User
from search import search_keywords

login = LoginManager(app)
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Resource': Resource, 'Category': Category}

@app.route("/", methods=['GET', 'POST'])
def home():
    user_id = current_user.get_id()
    user_is_admin = False
    if user_id:
        user = User.query.get(user_id)
        user_is_admin = user.is_admin

    all_resources = get_all_resources()
    all_categories = get_all_categories()
    category_filters = set(['Show All'])
    show_all = True
    all_institutions = get_all_institutions()
    all_resource_types = get_all_resource_types()
    all_ia_labels = ['Ambulatory/Discharge', 'Inpatient/ED', 'Both', 'Neither']
    total = len(all_resources)
    return render_template("home.html",
                            all_resources=all_resources,
                            all_categories=all_categories,
                            category_filters=category_filters,
                            show_all=show_all,
                            all_institutions=all_institutions,
                            all_resource_types=all_resource_types,
                            all_ia_labels=all_ia_labels,
                            total=total,
                            user_is_admin=user_is_admin)

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect('/')
    if request.method == 'GET':
        return render_template('signup.html')

    email = request.form['email']
    password = request.form['passwd']

    user_exists = User.query.filter_by(email=email).first()
    if user_exists:
        error = 'A user with that email already exists.'
        return render_template('signup.html', error=error)
    if not email.endswith('.edu'):
        error = 'Sorry, only .edu accounts are supported right now.'
        return render_template('signup.html', error=error)

    user = User(email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    login_user(user, remember=True)
    return redirect('/')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')
    if request.method == 'GET':
        return render_template('login.html')

    email = request.form['email']
    password = request.form['passwd']
    user = User.query.filter_by(email=email).first()
    if not user:
        error = 'Sorry, a user with that email doesn\'t exist.'
        return render_template('login.html', error=error)
    if not user.check_password(password):
        error = 'The password is incorrect. Please try again.'
        return render_template('login.html', error=error)

    login_user(user, remember=True)
    if user.is_admin:
        return redirect( url_for("admin") )

    return redirect('/')

@app.route("/reset", methods=['GET', 'POST'])
def confirm_email():
    if current_user.is_authenticated:
        return redirect('/')
    if request.method == 'GET':
        return render_template('reset.html')

    email = request.form['email']

    user_exists = User.query.filter_by(email=email).first()
    if not user_exists:
        error = 'Sorry, a user with that email doesn\'t exist.'
    return redirect('/reset-password')

@app.route("/reset-password", methods=['GET', 'POST'])
def reset_password():
    if request.method == 'GET':
        return render_template('reset_password.html')

    email = request.form['email']
    new_password = request.form['passwd']
    user = User.query.filter_by(email=email).first()
    user.set_password(new_password)
    db.session.add(user)
    db.session.commit()
    login_user(user, remember=True)
    return redirect('/')

@app.route("/logout")
def logout():
    logout_user()
    return redirect('/')

@app.route("/contribute", methods=['GET', 'POST'])
def contribute():
    all_categories = get_all_categories()[1:]
    all_institutions = get_all_institutions()
    all_types = get_all_resource_types()
    all_binary = get_all_binary()
    message = ''
    if request.method == 'POST':
        # print(request.form)
        r, message = add_contributed_resource(request.form)
        return render_template("contribute.html",
                                all_categories=json.dumps(all_categories),
                                all_institutions=all_institutions,
                                all_types=all_types,
                                all_binary=all_binary,
                                message=message)

    return render_template("contribute.html",
                            all_categories=json.dumps(all_categories),
                            all_institutions=all_institutions,
                            all_types=all_types,
                            all_binary=all_binary,
                            message='')

@app.route("/edit/<string:resource_id>", methods=['GET', 'POST'])
def edit(resource_id):
    # Need to implement
    user_id = current_user.get_id()
    user_is_admin = False
    if user_id:
        user = User.query.get(user_id)
        user_is_admin = user.is_admin
    if not user_is_admin:
        return Response(
            'Could not verify your access level for that URL.\n'
            'You have to login with proper credentials', 401)

    all_categories = get_all_categories()[1:]
    all_institutions = get_all_institutions()
    all_types = get_all_resource_types()
    all_binary = get_all_binary()
    if request.method == 'POST':
        # Update resource, but don't show yet
        if 'save' in request.form:
            msg = edit_entry(resource_id, request.form)
            print('Saved resource with ID: {}'.format(resource_id))

        # Update resource, then update 'show' to be true?
        elif 'save-approve' in request.form:
            msg = edit_entry(resource_id, request.form, approve=True)
            print('Saved & approved resource with ID: {}'.format(resource_id))

        return redirect(url_for('admin'))

    resource = get_resource_by_id(resource_id)
    note = ''
    if resource['show']:
        note = "Note: You are editing a resource that is already published. Any changes you save will be immediately viewable to users."
    else:
        note = "Note: You are editing a pending submission (not published). To make changes without publishing, press \"Save\". To publish the submission, press \"Save & Approve\"."
    return render_template("edit.html",
                            resource=resource,
                            all_categories=json.dumps(all_categories),
                            all_institutions=all_institutions,
                            all_types=all_types,
                            all_binary=all_binary,
                            note=note)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    # verify again that only admin users can access this page
    user_id = current_user.get_id()
    user_is_admin = False
    if user_id:
        user = User.query.get(user_id)
        user_is_admin = user.is_admin
    if not user_is_admin:
        return Response(
            'Could not verify your access level for that URL.\n'
            'You have to login with proper credentials', 401)
    pending_resources = get_pending_resources()
    published_resources = get_resource_query()
    published_extracted = False

    query_phrase = ''
    query_keywords = []
    pending_query = ''
    published_query = ''
    if request.method == 'POST':
        print(request.form)
        if 'published-searchbar-input' in request.form:
            query_phrase = request.form['published-searchbar-input'].strip()
            published_query = query_phrase
            query_keywords = query_phrase.split(' ')
            all_resources = extract_resources(published_resources)
            published_extracted = True
            all_resources = search_keywords(query_keywords, all_resources)
            published_resources = all_resources if len(query_keywords) > 0 else published_resources

        elif 'pending-searchbar-input' in request.form:
            query_phrase = request.form['pending-searchbar-input'].strip()
            pending_query = query_phrase
            query_keywords = query_phrase.split(' ')
            all_resources = search_keywords(query_keywords, pending_resources)
            pending_resources = all_resources if len(query_keywords) > 0 else pending_resources


    if not published_extracted:
        published_resources = extract_resources(published_resources)

    total = len(published_resources)
    total_pending = len(pending_resources)

    return render_template("admin.html",
                            pending_resources=pending_resources,
                            published_resources=published_resources,
                            total_pending=total_pending,
                            total=total,
                            pending_query=pending_query,
                            published_query=published_query)

@app.route("/update_resource/<string:resource_id>", methods=["POST"])
def update_resource(resource_id):
    # Need to implement
    user_id = current_user.get_id()
    user_is_admin = False
    if user_id:
        user = User.query.get(user_id)
        user_is_admin = user.is_admin
    if not user_is_admin:
        return Response(
            'Could not verify your access level for that URL.\n'
            'You have to login with proper credentials', 401)

    print(request.form)
    if 'approve' in request.form:
        print('Approved resource with ID: {}'.format(resource_id))
        approve_entry(resource_id)

    elif 'delete' in request.form:
        print('Deleted resource with ID: {}'.format(resource_id))
        delete_resource(resource_id=resource_id)
        pass

    elif 'unapprove' in request.form:
        print('Unapproved resource with ID: {}'.format(resource_id))
        unapprove_entry(resource_id)

    return redirect(url_for('admin'))

@app.route("/sort")
def sort():
    all_resources = get_all_resources()
    all_categories = get_all_categories()
    return render_template("home.html", all_resources=all_resources, all_categories=all_categories)

@app.route("/resources", methods=['GET', 'POST'])
def resources():

    print("Search request: {}".format(request.args))

    # Keyword search
    query_phrase = ''
    query_keywords = []

    if request.args.get('searchbar-input'):
        query_phrase = request.args.get('searchbar-input').strip()
        query_keywords = query_phrase.split(' ')
        # do something

    # Institution search
    all_institutions = get_all_institutions()
    institution = ''
    if request.args.get('institution-search-input'):
        institution = request.args.get('institution-search-input')

    # Sort
    sortby = None
    if request.args.get('sortby-input'):
        if request.args.get('sortby-input') == 'default':
            sortby = None
        else:
            sortby = request.args.get('sortby-input')

    # I/A filter
    all_ia_labels = ['Ambulatory/Discharge', 'Inpatient/ED', 'Both', 'Neither']
    active_ia = None
    if request.args.get('ia-input'):
        if request.args.get('ia-input') == 'All Resources':
            active_ia = None
        else:
            active_ia = request.args.get('ia-input')
            all_ia_labels = ['All Resources'] + all_ia_labels

    # Resource type
    all_resource_types = get_all_resource_types()
    all_resource_types = set(all_resource_types)
    all_resource_types.discard(None)
    all_resource_types = sorted(list(all_resource_types))
    resource_type = None
    if request.args.get('resource-type-input'):
        if request.args.get('resource-type-input') == 'All Resources':
            resource_type = None
        else:
            resource_type = request.args.get('resource-type-input')
            all_resource_types = ['All Resources'] + all_resource_types

    # Category filter
    all_categories = get_all_categories()
    category_filters = set()

    for cat in all_categories:
        if request.args.get(cat):
            category_filters.add(cat)

    show_all = False
    if 'Show All' in category_filters:
        show_all = True

    # Filter all resources by form filters
    all_resources = get_resource_query()
    if not show_all:
        all_resources = filter_by_category(all_resources, category_filters)

    if len(institution) > 0:
        all_resources = filter_by_institution(all_resources, institution)

    if resource_type:
        all_resources = filter_by_type(all_resources, resource_type)

    if sortby:
        all_resources = filter_sort(all_resources, sortby)

    if active_ia:
        all_resources = filter_by_ia(all_resources, active_ia)

    all_resources = extract_resources(all_resources)

    final_resources = search_keywords(query_keywords, all_resources)

    all_resources = final_resources if len(query_keywords) > 0 else all_resources
    total = len(all_resources)

    return render_template("home.html",
                            all_resources=all_resources,
                            all_categories=all_categories,
                            category_filters=category_filters,
                            show_all=show_all,
                            sortby=sortby,
                            all_institutions=all_institutions,
                            active_institution=institution,
                            all_resource_types=all_resource_types,
                            active_resource_type=resource_type,
                            all_ia_labels=all_ia_labels,
                            active_ia=active_ia,
                            search_query=query_phrase,
                            total=total)

@app.route("/about")
def about():
    return render_template("about.html")

# app.secret_key = os.urandom(12)
app.secret_key = '61:72:6c:65:6e:65'
if __name__ == "__main__":
    host = sys.argv[-1]
    app.run(host=host, port=8000)
