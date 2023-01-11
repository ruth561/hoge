from flask import Flask
import platform
from smb.SMBConnection import SMBConnection
import io
import json

# gets information to connect to smb server. 
try:
    json_file = open("backend/setting.json", "r")
except OSError as e:
    print("[ ERROR ] Please create a file \"backend/setting.json\".") 
    exit() 
json_data = json.load(json_file)
json_file.close()

# creates an object that controls the connection to the smb server. 
nas_conn = SMBConnection(
    json_data["user"], 
    json_data["password"], 
    platform.uname().node, 
    "IEWIN7")
nas_conn.connect(json_data["server_ip"], json_data["server_port"])

app = Flask(__name__)

@app.route("/api")
def index():
    return "Hello, world!"

# returns the list of files in "folder"
@app.route("/nas/<folder>/")
def list_search(folder):
    global nas_conn
    try:
        items = nas_conn.listPath(folder, "")
        res = ""
        for item in items:
            res += item.filename
            res += "\r\n"
        return res
    except:
        return f"Error. Sorry, NAS doesn't have such a solder \"{folder}\"."

# return the data of file at "folder/path"
@app.route("/nas/<folder>/<path>")
def get_file(folder, path):
    global nas_conn
    with io.BytesIO() as file:
        nas_conn.retrieveFile(folder, path, file)
        file.seek(0)
        return file.read().decode()