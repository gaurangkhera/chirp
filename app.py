import uuid
from os import path
from flask import flash, redirect, render_template, request, url_for, abort
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from hack import app, create_db,db, socketio
from hack.forms import LoginForm, PostForm, RegForm, SendMessageForm
from hack.models import Follow, Post, User, ChatMessage
from post_handler import get_lines
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VideoGrant
import os
from dotenv import load_dotenv

load_dotenv()
twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
twilio_api_key_sid = os.getenv('TWILIO_API_KEY_SID')
twilio_api_key_secret = os.getenv('TWILIO_API_KEY_SECRET')


load_dotenv()
create_db(app)

@app.route('/')
def home():
    all_posts = Post.query.all()
    auth_posts = []
    return render_template('index.htm', all_posts=all_posts, auth_posts=auth_posts)

@app.route('/post', methods=['GET', 'POST'])
@login_required
def post():
    form = PostForm()
    if form.validate_on_submit():
        new_post = Post(img=str(uuid.uuid1()) + '_' + form.img.data.filename, content=form.content.data, title=form.title.data, poster=current_user.username)
        form.img.data.save(path.join('hack/static/post_imgs/', new_post.img))
        db.session.add(new_post)
        db.session.commit()
        flash('Post successful.', 'success')
        return redirect(url_for('home'))
    return render_template('post.htm', form=form)

@app.route('/posts')
def posts():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('posts.htm', posts=posts, get_lines=get_lines)

@app.route('/posts/<id>')
def view_post(id):
    post = Post.query.filter_by(id=id).first()
    return render_template('indi_post.htm', post=post)

@app.route('/users/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first()
    follow = Follow.query.filter_by(follower_id=current_user.username, followed_id=user.username).first()
    return render_template('profile.htm', user=user, follow=follow)    

@app.route('/follow/<username>')
@login_required
def follow_user(username):
    user = User.query.filter_by(username=username).first()
    follow = Follow.query.filter_by(follower_id=current_user.username, followed_id=user.username).first()
    if not follow and current_user.username != user.username:
        current_user.follow(user)
        db.session.add(current_user)
        db.session.add(user)
        db.session.commit()
        flash(f'You are now following {user.username}.', 'success')
    elif current_user.username == user.username:
        flash('You cannot follow yourself.', 'error')
    else:
        flash('You are already following this user.', 'error')
    return redirect(url_for('profile', username=user.username))

@app.route('/unfollow/<username>')
@login_required
def unfollow_user(username):
    user = User.query.filter_by(username=username).first()
    follow = Follow.query.filter_by(follower_id=current_user.username, followed_id=user.username).first()
    if follow and current_user.username != user.username:
        current_user.unfollow(user)
        db.session.add(current_user)
        db.session.add(user)
        db.session.commit()
        flash(f'You are now not following {username}.', 'success')
    elif current_user.username == user.username:
        flash('You cannot unfollow yourself.', 'error')
    else:
        flash('You are not following this user.', 'error')
    return redirect(url_for('profile', username=user.username))

@app.route('/reg', methods=['GET', 'POST'])
def reg():
    form = RegForm()
    mess=''
    if form.validate_on_submit():
        email = form.email.data
        username = form.username.data
        password = form.password.data
        img = form.img.data
        file_name = str(uuid.uuid1()) + img.filename
        img.save(path.join('hack/static/users/',file_name))
        user = User.query.filter_by(email=email).first()
        usrname = User.query.filter_by(username=username).first()
        if user:
            mess='Another account with this email already exists.'
        elif usrname:
            mess='Another account with this username already exists.'
        else:
            new_user = User(email=email, username=username, password=generate_password_hash(password), about=form.about.data, img=file_name)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect('/')
    return render_template('reg.htm', form=form, mess=mess)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    mess=''
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        check_username = User.query.filter_by(username=email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                return redirect(url_for('home'))
            else:
                flash('Incorrect password.', 'error')  
        elif check_username:
            if check_password_hash(check_username.password, password):
                login_user(check_username, remember=True)
                return redirect(url_for('home'))
            else:
                flash('Incorrect password.', 'error')
    return render_template('login.htm', mess=mess, form=form)

@app.route('/dms')
@login_required
def dms():
    return render_template('dms.htm')

@app.route('/chat/<username>', methods=['GET', 'POST'])
@login_required
def chat(username):
    user = User.query.filter_by(username=username).first()
    return render_template('chat.htm',user=user)

@socketio.on('my event')
def handle_msg(json, methods=['GET', 'POST']):
    print(json)
    msg = ChatMessage(sender=json['sender'], receiver=json['receiver'], message=json['msg'])
    db.session.add(msg)
    db.session.commit()
    socketio.emit('my response', json, callback='hehaushuas')
    
@socketio.on('upload')
def upload(json, methods=['GET', 'POST']):
    print(json)
    msg = ChatMessage(message=json['file'], sender=json['sender'], receiver=json['receiver'])
    db.session.add(msg)
    db.session.commit()
    socketio.emit('upload success', json, callback='hejeujdiu')
    
@app.route('/vc_login', methods=['POST'])
@login_required
def vc_login():
    username = request.get_json(force=True).get('username')
    print(username)
    room1 = request.get_json(force=True).get('id_t')
    print(room1)
    if not username:
        abort(401)

    token = AccessToken(twilio_account_sid, twilio_api_key_sid,
                        twilio_api_key_secret, identity=username)
    token.add_grant(VideoGrant(room=room1+'hey'))
    return {'token': token.to_jwt()}



@app.route('/chat/<username>')
@login_required
def show_chats(username):
    if username != '000':
        user = User.query.filter_by(username=username)
    else: 
        user = 'No channels.'
    return render_template('chat.htm', user=user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0')
