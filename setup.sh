#! /bin/bash

export FLASK_APP=backend/main.py
export FLASK_ENV=development

if [ ! -e "backend/setting.json" ] || [ "$1" = "config" ]; then
    # creates a setting file "backend/setting.json"
    python3 backend/config.py
fi

# ampersand before flask run backgrounds the process
# i.e., 'yarn start' is fired after 'flask run'
(cd frontend 
yarn start) & 
flask run
