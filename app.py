import os
import requests

from flask import Flask, request, g, session, request, redirect, url_for, render_template, Markup
from flask import render_template_string
from flask_restful import Api, Resource, request

from flask_github import GitHub

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URI = 'sqlite:////tmp/github-flask.db'
SECRET_KEY = os.getenv("SECRET_KEY", "FDSLKFJSLKDFJDSLKF")
DEBUG = os.getenv("DEBUG", False)

# test data
USERS = []

# setup flask
app = Flask(__name__)
app.config.from_object(__name__)

# setup github-flask
app.config['GITHUB_CLIENT_ID'] = os.getenv("CLIENT_ID")
app.config['GITHUB_CLIENT_SECRET'] = os.getenv("CLIENT_SECRET")

github = GitHub(app)

#github.authorize('admin:org')
SCOPE = 'read:org'
# setup flask-restful
api = Api(app)

# setup sqlalchemy
engine = create_engine(app.config['DATABASE_URI'])
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

# Helpers for Github OAuth integration
def init_db():
    Base.metadata.create_all(bind=engine)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(200))
    github_access_token = Column(String(200))

    def __init__(self, github_access_token):
        self.github_access_token = github_access_token


@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])


@app.after_request
def after_request(response):
    db_session.remove()
    return response


@github.access_token_getter
def token_getter():
    user = g.user
    if user is not None:
        return user.github_access_token

@app.route('/success')
@github.authorized_handler
def success():
    global USERS
    members = github.get('orgs/imapex/members')
    member_ids = [m['login'] for m in members]
    USERS = [{"githubuser": str(u)} for u in member_ids]
    print USERS

    return render_template_string("User list updated based on org membership!")


@app.route('/authorized')
@github.authorized_handler
def authorized(access_token):
    next_url = request.args.get('next') or url_for('success')
    if access_token is None:
        return redirect(next_url)

    user = User.query.filter_by(github_access_token=access_token).first()

    if user is None:
        user = User(access_token)
        db_session.add(user)
    user.github_access_token = access_token
    db_session.commit()

    session['user_id'] = user.id
    print("Updating users requested by: {}".format(session['user_id']))
    return redirect(next_url)


@app.route('/update')
def login():
    return github.authorize(scope=SCOPE)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))


@app.route('/user')
def user():
    return str(github.get('user'))


@app.route('/')
def index():

    cals = {}
    for u in USERS:
        resp = requests.get('https://github.com/users/{}/contributions'.format(u['githubuser'])).text
        cals[u['githubuser']] = Markup(resp)

    return render_template('index.html', cals=cals)

class AddMember(Resource):
    def post(self):
        global USERS
        req = request
        print USERS
        if 'githubuser' in req.json.keys():
            if req.json not in USERS:
                USERS.append(req.json)
        print USERS

api.add_resource(AddMember, '/api/users/add')


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', debug=DEBUG)