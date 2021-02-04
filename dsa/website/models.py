from flask import url_for
from dsa import db
from dsa.auth.models import Member


# a calendar event (meeting, etc.)
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256),nullable=False)
    start = db.Column(db.DateTime, nullable=False,server_default=db.func.current_timestamp())
    

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    

class Election(db.Model):
    id = db.Column(db.Integer, primary_key=True)
