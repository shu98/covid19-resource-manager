from app import db

from models import User

email = 'insert_email_here'
password = 'insert_password_here'

admin_user = User(email=email)
admin_user.set_password(password)
admin_user.is_admin = True

db.session.add(admin_user)
db.session.commit()