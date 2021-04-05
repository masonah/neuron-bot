from . import db
from datetime import datetime

# Base = declarative_base()


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    joined_date = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow)
    slack_user_id = db.Column(db.CHAR(32), unique=True, index=True, nullable=False)

    def __repr__(self):
        return '<User {}>'.format(self.slack_user_id)

# def __init__(self):
#     self._slack_user_id = ''
#     self._first_name = ''
#     self._last_name = ''
#     self_email = ''
#
# def get_user_id(self):
#     return self._slack_user_id
#
# def set_user_id(self, slack_user_id):
#     self._slack_user_id = slack_user_id
#
# def get_first_name(self):
#     return self._first_name
#
# def set_first_name(self, name):
#     self._first_name = name
#
# def get_last_name(self):
#     return self._first_name
#
# def set_last_name(self, name):
#     self._first_name = name
#
# def get_email(self):
#     return self._email
#
# def set_email(self, email):
#     self._email = email
#
# slack_user_id = property(get_user_id(), set_user_id())
# first_name = property(get_first_name(), set_first_name())
# last_name = property(get_last_name(), set_last_name())
# email = property(get_email(), set_email())
