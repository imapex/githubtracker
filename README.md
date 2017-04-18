# github-tracker

[![Build Status](http://drone.green.browndogtech.com/api/badges/imapex/githubtracker/status.svg)](http://drone.green.browndogtech.com/imapex/githubtracker)

A super simple application to graph multiple users Github contribution activity on a single page


## Running

    pip install -r requirements.txt
    python app.py

## Adding Users

Users can be added by simply sending a POST request to /api/users/add with the following data

    {"githubuser": "mygithubid"}


