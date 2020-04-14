# import pandas as pd
import numpy as np
import ast
from datetime import datetime

from app import db
from models import Resource, Category, resource_categories

def add_contributed_resource(form):
    params = ['title', 'link', 'institution', 'categories', 'description', 'submitter', 'ia', 'resource_type']
    inputs = {}
    for param in params:
        inputs[param] = form[param]

    date_added = datetime.utcnow()
    new_resource = Resource(title=inputs['title'], institution=inputs['institution'], 
                                   description=inputs['description'], link=inputs['link'], 
                                   submitter=inputs['submitter'], iped_ad=inputs['ia'], 
                                   resource_type=inputs['resource_type'], date_added=date_added, 
                                   show=False)
    categories = ast.literal_eval(inputs['categories'])
    for category in categories:
        cat = category['value']
        cat_exists = db.session.query(Category.id).filter_by(name=cat).scalar() is not None

        ## adding to database 
        if not cat_exists:
            print('adding to database')
            new_category = Category(name=cat, slug=cat.lower().replace(' ', '_'))
            db.session.add(new_category)
            db.session.commit()
        else:
            print('cat exists')
            new_category = Category.query.get(db.session.query(Category.id).filter_by(name=cat).all()[0])
        
        new_resource.categories.append(new_category)
    
    ## check for duplicate resource
    error_message = 'Thank you! Your submission has been submitted for review.'
    try:
        db.session.add(new_resource)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        error_message = 'Duplicate already exists in the database. Resource not saved. Please ensure that the title and link you submit are unique.'
        print('ERROR: Duplicate resource')
    
    return new_resource, error_message

def extract_resource_info(resource):
    return get_resource_dict(resource)

def extract_resources(unextracted):
    all_resources = []
    for resource in unextracted:
        d = extract_resource_info(resource)
        if d['show']:
            all_resources.append(d)
    return all_resources

def get_all_resources(alpha=False):
    resources_list = []
    all_resources = Resource.query
    if alpha:
        all_resources = all_resources.order_by(Resource.title)
    all_resources = all_resources.all()
    for resource in all_resources:
        d = get_resource_dict(resource)
        if d['show']:
            resources_list.append(d)
    
    return resources_list

def get_pending_resources(alpha=False):
    resources_list = []
    all_resources = Resource.query
    if alpha:
        all_resources = all_resources.order_by(Resource.title)
    all_resources = all_resources.all()
    for resource in all_resources:
        d = get_resource_dict(resource)
        if not d['show']:
            resources_list.append(d)
    
    return resources_list

def get_resource_by_id(resource_id):
    resource = Resource.query.get(resource_id)
    return get_resource_dict(resource)

def get_resource_dict(resource):
    d = {}
    d['id'] = resource.id
    d['submitter'] = resource.submitter 
    d['title'] = resource.title
    d['link'] = resource.link
    d['institution'] = resource.institution
    d['date_added'] = resource.date_added.strftime('%m/%d/%y')
    d['description'] = resource.description
    d['iped_ad'] = resource.iped_ad
    d['resource_type'] = resource.resource_type
    d['categories'] = []
    categories = resource.categories
    for category in categories:
        d['categories'].append(category.name)
    d['show'] = resource.show
    return d

def get_all_categories():
    categories_list = []
    all_categories = Category.query.order_by(Category.name).all()
    query = get_resource_query()
    for category in all_categories:
        if filter_by_category(query, [category.name]).count() > 0:
            categories_list.append(category.name)
    categories_list = ['Show All'] + categories_list
    return categories_list

def get_all_institutions():
    institutions = db.session.query(Resource.institution.distinct().label('title')).all()
    all_institutions = [i[0] for i in institutions]
    return all_institutions

def get_all_resource_types():
    query = db.session.query(Resource.resource_type.distinct().label("name"))
    types = [row.name for row in query.all()] 
    return types

def get_all_binary():
    query = db.session.query(Resource.iped_ad.distinct().label("name"))
    binary = [row.name for row in query.all()]
    return binary

def get_resource_query():
    return Resource.query

def filter_by_category(query, categories):
    all_resources_unextracted = query.filter(Resource.categories.any(Category.name.in_(categories)))
    return all_resources_unextracted

def filter_by_institution(query, institutions):
    all_resources_unextracted = query.filter_by(institution=institutions)
    return all_resources_unextracted

def filter_sort(query, sort):
    if sort == 'alpha':
        all_resources = query.order_by(Resource.title)
    if sort == 'reverse-alpha':
        all_resources = query.order_by(Resource.title.desc())
    if sort == 'most-recently-added':
        all_resources = query.order_by(Resource.date_added.desc())
    if sort == 'most-upvoted':
        all_resources = query.order_by(Resource.upvotes.desc())
    return all_resources

def filter_by_type(query, resource_type):
    all_resources_unextracted = query.filter_by(resource_type=resource_type)
    return all_resources_unextracted

def filter_by_ia(query, ia):
    all_resources_unextracted = query.filter_by(iped_ad=ia)
    return all_resources_unextracted

def edit_entry(resource_id, form, approve=False, unapprove=False):
    params = ['title', 'link', 'institution', 'categories', 'description', 'submitter', 'ia', 'resource_type']
    inputs = {}
    for param in params:
        inputs[param] = form[param]

    date_added = datetime.utcnow()

    resource = Resource.query.get(resource_id)
    resource.title = inputs['title']
    resource.link = inputs['link']
    resource.institution = inputs['institution']
    resource.description = inputs['description']
    resource.submitter = inputs['submitter']
    resource.iped_ad = inputs['ia']
    resource.resource_type = inputs['resource_type']
    
    if approve:
        resource.show = True
    
    if unapprove:
        resource.show = False

    resource.categories = []

    categories = ast.literal_eval(inputs['categories'])
    for category in categories:
        cat = category['value']
        cat_exists = db.session.query(Category.id).filter_by(name=cat).scalar() is not None

        ## adding to database 
        if not cat_exists:
            print('adding to database')
            new_category = Category(name=cat, slug=cat.lower().replace(' ', '_'))
            db.session.add(new_category)
            db.session.commit()
        else:
            print('cat exists')
            new_category = Category.query.get(db.session.query(Category.id).filter_by(name=cat).all()[0])
        
        resource.categories.append(new_category)

    db.session.commit()
    return 'Edited resource with id {}'.format(resource_id)

def approve_entry(resource_id):
    resource = Resource.query.get(resource_id)
    resource.show = True
    db.session.commit()
    return 'Approved resource with id {}'.format(resource_id)

def unapprove_entry(resource_id):
    resource = Resource.query.get(resource_id)
    resource.show = False
    db.session.commit()
    return 'Unapproved resource with id {}'.format(resource_id)

def delete_all_entries():
    num_r = Resource.query.delete(synchronize_session='evaluate')
    num_c = Category.query.delete(synchronize_session='evaluate')
    num_all = resource_categories.delete(synchronize_session='evaluate')
    db.session.commit()
    message = 'Deleted {} resources and {} categories and {} both'.format(num_r, num_c, num_all)
    print(message)
    return message

def delete_resource(name=None, resource_id=None):
    if name:
        resource = db.session.query(Resource).filter(Resource.title==name).first()
    elif resource_id:
        resource = Resource.query.get(resource_id)
    resource.categories = []
    db.session.delete(resource)
    db.session.commit()
    return 'Successfully removed {}'.format(name)