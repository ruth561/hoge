from flask import Flask
import platform
from nas import NAS
import io
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
exit()

app = Flask(__name__)

@app.route("/api")
def index():
    return "Hello, world!"

# returns the list of files in "folder"
@app.route("/nas/<folder>/")
def list_search(folder):
    global nas
    try:
        items = nas.listPath(folder, "")
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
