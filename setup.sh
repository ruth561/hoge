#! /bin/bash

export FLASK_APP=backend/main.py
export FLASK_ENV=development

# ampersand before flask run backgrounds the process
# i.e., 'yarn start' is fired after 'flask run'
(cd frontend 
yarn start) & 
flask run
