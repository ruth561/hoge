from flask import Flask
from nas import NAS
import json

# gets information to connect to smb server. 
try:
    json_file = open("backend/setting.json", "r")
except OSError as e:
    print("[ BACKEND ERROR ] Please create a file \"backend/setting.json\".") 
    exit() 
json_data = json.load(json_file)
json_file.close()

nas = NAS(
    json_data["user"],
    json_data["password"], 
    json_data["server_ip"], 
    json_data["server_port"],
    "hoge", 
    "backend/tmp"
)


# Web Application
app = Flask(__name__)

@app.route("/api")
def index():
    return "Hello, world!"

# return the data of file at "folder/path"
@app.route("/nas/<path>")
def get_file(path):
    global nas
    return nas.get_file(path)
