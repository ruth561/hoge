from flask import Flask
from nas import NAS
import json

# gets information to connect to smb server. 
try:
    json_file = open("backend/setting.json", "r")
except OSError as e:
    print("[ ERROR ] Please create a file \"backend/setting.json\".") 
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

@app.route("/api/all")
def get_all_metadata():
    global nas
    dirs, _ = nas.ls("")
    d = dict()
    for dir in dirs:
        data = nas.get_file(dir + "/metadata.json")
        if data:
            d[dir] = json.loads(data)
    return json.dumps(d, indent=4, ensure_ascii=False)


@app.route("/api/<seminar_id>")
def get_metadata(seminar_id):
    global nas
    dirs, _ = nas.ls("/")
    if seminar_id in dirs:
        data = nas.get_file(seminar_id + "/metadata.json")
        if data:
            return data
    return b"Nothing"

# return the data of file at "folder/path"
@app.route("/nas/<path:path>")
def get_file(path):
    global nas
    data = nas.get_file(path)
    if data:
        return data
    return b"Nothing"