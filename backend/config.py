# This file creates a file "setting.json".
# This program is assumed to run from hoge/ dir.
import json

json_data = dict()

print("[ Configure connection settings to the NAS ]")
print("Enter the user name to connect to the NAS.")
json_data["user"] = input("user > ")

print("Enter the password for the user.")
json_data["password"] = input("password > ")

print("Enter the ip address of the NAS.")
json_data["server_ip"] = input("server_ip > ")

print("Enter the port number of the NAS. (basically, just type in 139)")
json_data["server_port"] = input("server_port > ")

with open("backend/setting.json", "w") as json_file:
    json.dump(json_data, json_file, indent=4)
