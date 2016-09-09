from flask import Flask, render_template, Markup
from flask_restful import Api, Resource, request
import BeautifulSoup
import requests
import os

# TODO need to add data persistence

USERS = [{"githubuser": "kecorbin"}]


app = Flask(__name__)
api = Api(app)

@app.route('/')
def contributions():
    cals = {}
    for u in USERS:
        resp = requests.get('https://github.com/users/{}/contributions'.format(u['githubuser'])).text
        soup = BeautifulSoup.BeautifulSoup(resp)
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
    app.run(host='0.0.0.0', debug=os.getenv("FLASK_DEBUG"))