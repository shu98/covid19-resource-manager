import pandas as pd
import numpy as np
import re
from datetime import datetime

from app import db
import models

## FOR PROTOCOLS/GUIDELINES
df = pd.read_csv('static/data/initial_2.csv', usecols=[0,1,2,3,4,5,6,7])

## FOR OTHER RESOURCES
# df = pd.read_csv('static/data/initial_other.csv', usecols=[0,1,2,3,4,5,6,7])

for index, row in df.iterrows():
    print(index)
    link = row['Link']
    if type(link) == float:
        ## No given link
        continue
    title = row['Title']
    institution = row['Source/Institution'].strip()

    print(title)

    if pd.isnull(df.iloc[index,6]):
        description = ''
    else:
        description = row['Notes']
    if not pd.isnull(df.iloc[index,7]):
        date = row['Date']
        try:
            date_added = datetime.strptime(date, '%m/%d/%y')
        except Exception as e:
            date_added = datetime.strptime(date, '%B %Y')
    else:
        date_added = datetime.utcnow()
    submitter = 'Covid-19 Guideline Clearinghouse'
    show = True

    if not pd.isnull(df.iloc[index,3]):
        iped_ad = row['Inpatient/Ambulatory']
        if len(iped_ad.split(', ')) > 1:
            iped_ad = 'Both'
        if iped_ad == 'None' or iped_ad == None:
            iped_ad = 'Neither'
    else:
        iped_ad = 'Neither'

    resource_type = row['Resource Type']

    new_resource = models.Resource(title=title, institution=institution, description=description, 
                                        link=link, submitter=submitter, date_added=date_added, show=show,
                                        iped_ad=iped_ad, resource_type=resource_type)

    cat_all = row['Tags'] if type(row['Tags']) != float else 'Miscellaneous'
    # cat = row['Type']
    # cats = cat.split(', ')
    cats = re.split(', |/', cat_all)
    
    for cat in cats:
        if len(cat) == 0:
            continue
        cat = cat.strip()
        cat = cat.title() if len(cat.split()) > 1 and 'OB' not in cat and 'PPE' not in cat else cat
        cat = cat.capitalize() if len(cat.split()) == 1 and not cat.isupper() else cat
        print(cat)
        cat_exists = db.session.query(models.Category.id).filter_by(name=cat).scalar() is not None 

        ## adding to database 
        if not cat_exists:
            new_category = models.Category(name=cat, slug=cat.lower().replace(' ', '_'))
            db.session.add(new_category)
            db.session.commit()
        else:
            new_category = models.Category.query.get(db.session.query(models.Category.id).filter_by(name=cat).all()[0])

        print(new_category)
        
        new_resource.categories.append(new_category)

    new_category, cats = None, None

    ## check for duplicate resource
    try:
        db.session.add(new_resource)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print('ERROR: Duplicate resource')

