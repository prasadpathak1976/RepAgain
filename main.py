from flask import Flask, render_template, url_for, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail
#from werkzeug import secure_filename

import json
import os
import smtplib
import math

local_server = True
with open('config.json', 'r') as c:
    params = json.load(c)["params"]
app = Flask(__name__)

app.secret_key = 'super-secret-key'
#app.config['UPLOAD_FOLDER'] = params['upload_loation']
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD=  params['gmail-pass']
)
mail = Mail(app)
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']
db = SQLAlchemy(app)


class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80),  nullable=True)
    phone_num = db.Column(db.String(12),  nullable=True)
    msg = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(50), nullable=True)
    date = db.Column(db.String(20), nullable=True)


class Post(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80),  nullable=True)
    tagline = db.Column(db.String(50), nullable=True)
    content = db.Column(db.String(120),  nullable=True)
    slug = db.Column(db.String(50), nullable=True)
    img_file = db.Column(db.String(12), nullable=True)
    date = db.Column(db.String(20), nullable=True)


@app.route("/")
def home():
    posts = Post.query.filter_by().all()
    # return str(posts)
    last = math.ceil(len(posts)/int(params['no_of_posts']))

    # posts = posts[]

    page = request.args.get('page')

    if(not str(page).isnumeric()):
        page = 1
    page = int(page)
    # return str(page)
    # return str(int(params['no_of_posts']))
    if(page==1):
        posts = posts[0: page*int(params['no_of_posts'])]
    else:
        posts = posts[page+int(params['no_of_posts']-1): page*int(params['no_of_posts'])]
    # return str(posts)
    if(page==1):
        prev = "#"
        next = "/?page=" + str(page+1)
    elif(page==last):
        prev = "/?page=" + str(page - 1)
        next = "#"
    else:
        prev = "/?page=" + str(page - 1)
        next = "/?page=" + str(page + 1)

    return render_template('index.html', params=params, posts=posts, prev=prev, next=next)


@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    #post = {"title": "prasad"}
    posts = Post.query.filter_by(slug=post_slug).first()

    return render_template('post.html', params=params, post=posts)


@app.route("/about")
def about():
    return render_template('aboutus.html', params=params)


@app.route("/edit/<string:sno>", methods=['GET', 'POST'])
def edit(sno):
    # return request.method
    if sno:
        sno = sno
    else:
        sno = "0"
    if ('user' in session and session['user'] == params['admin_user']):

        if request.method == 'POST':
           # return request.method
            btitle = request.form.get('title')
            tagline = request.form.get('tagline')
            content = request.form.get('content')
            img_file = request.form.get('img_file')
            slug = request.form.get('slug')
            date = datetime.now()
            # return btitle
            if sno == '0':
                post = Post(title=btitle, tagline=tagline, content=content, img_file=img_file, slug=slug, date=date)
                db.session.add(post)
                db.session.commit()
                # return redirect('/dashboard')
            else:
                post = Post.query.filter_by(sno=sno).first()
                post.title = btitle
                post.tagline = tagline
                post.content = content
                post.img_file = img_file
                post.slug = slug
                db.session.commit()
                return redirect('/edit/'+sno)

        post = Post.query.filter_by(sno=sno).first()
        return render_template('edit.html', params=params, post=post, sno=sno)


@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if('user' in session and session['user'] == params['admin_user']):
        posts = Post.query.all()
        return render_template('dasboard.html', params=params, posts=posts)

    if request.method == 'POST':
        username = request.form.get('uname')
        password = request.form.get('pass')
        if(username == params['admin_user'] and password == params['admin_password']):
            session['user'] = username
            posts = Post.query.all()
            return render_template('dasboard.html', params=params, posts=posts)

    return render_template('login.html', params=params)


@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/dashboard')


@app.route("/delete/<string:sno>", methods=['GET', 'POST'])
def delete(sno):
    #return sno
    if ('user' in session and session['user'] == params['admin_user']):
         post = Post.query.filter_by(sno=sno).first()
         db.session.delete(post)
         db.session.commit()

    return redirect('/dashboard')


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if (request.method == 'POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        phone_num = request.form.get('phone_num')
        msg = request.form.get('msg')
        entry = Contacts(name=name, email=email, phone_num=phone_num, msg=msg, date=datetime.now())
        db.session.add(entry)
        db.session.commit()
        """"
        mail.send_message('New message from ' + name,
                          sender=email,
                          recipients=[params['gmail-user']],
                          body=msg + "\n" + phone_num
                          )
         """

    return render_template('contact.html', params=params)


app.run(debug=True)