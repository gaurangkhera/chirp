from hack import db,login_manager
from flask import abort
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin
from sqlalchemy.sql import func

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.String, db.ForeignKey('user.username'))
    followed_id = db.Column(db.String, db.ForeignKey('user.username'))
    
class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String)
    date_sent = db.Column(db.String, server_default=func.now())
    file = db.Column(db.String)
    sender = db.Column(db.String, db.ForeignKey('user.username'))
    receiver = db.Column(db.String, db.ForeignKey('user.username'))

class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key = True)
    img = db.Column(db.String)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String(64),index=True)
    password = db.Column(db.String)
    about = db.Column(db.String)
    posts = db.relationship('Post', backref='user')
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('followers', lazy='joined'))
    followers = db.relationship('Follow',
                              foreign_keys=[Follow.followed_id],
                              backref=db.backref('followed', lazy='joined'))
    msg_sender = db.relationship('ChatMessage', foreign_keys=[ChatMessage.receiver], backref=db.backref('msg_receiver', lazy='joined'))
    msg_receiver = db.relationship('ChatMessage', foreign_keys=[ChatMessage.sender], backref=db.backref('msg_sender', lazy='joined'))
          
    def follow(self, user):
        new_follow = Follow(follower_id=self.username, followed_id=user.username)
        db.session.add(new_follow)
        
    def unfollow(self, user):
        follow = Follow.query.filter_by(follower_id=self.username, followed_id=user.username).first()
        db.session.delete(follow)
                
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.String)
    title = db.Column(db.String)
    content = db.Column(db.String)
    poster = db.Column(db.String, db.ForeignKey('user.id'))
    date_posted = db.Column(db.String, server_default=func.now())
    

    
