from flask import Flask
import platform
from smb.SMBConnection import SMBConnection
from smb.base import SharedFile, OperationFailure
import os
import re
from typing import Union, Tuple, List


class NAS:
    def __init__(self, uname: str, passwd: str, server_ip: str, server_port: int, 
                 shared_folder_name: str, tmp_dir_path: str):
        self.uname                  = uname
        self.passwd                 = passwd
        self.server_ip              = server_ip
        self.server_port            = server_port
        self.shared_folder_name     = shared_folder_name
        self.tmp_dir_path           = tmp_dir_path + "/"
        self.conn: SMBConnection    = None
        self.nas_data: dict[str, SharedFile]    = dict()

        self.connect()
        self.check()
        self.synchronize("")
        print("Synchronization with NAS is completed.")

        print(self.ls("////01"))


    # connect to NAS
    def connect(self) -> SMBConnection:
        try:
            self.conn = SMBConnection(
                self.uname, 
                self.passwd, 
                platform.uname().node, 
                "IEWIN7"
            )
            self.conn.connect(self.server_ip, self.server_port)
            print("Successfully connected to NAS")
        except Exception as e:
            print(f"[ ERROR ] Failed to connect to the NAS ({self.server_ip}, {self.server_port}). ")
            exit()
    

    # check the settings are collect
    def check(self):
        for shared_dev in self.conn.listShares():
            if self.shared_folder_name == shared_dev.name:
                break
        else:
            print(f"[ Error ] Such a folder \"{self.shared_folder_name}\" doesn't exit in NAS.")
            exit()


    # return a tuple that (file list, dir list)
    def ls(self, path: str) -> Union[None, Tuple[List[str], List[str]]]:
        path = re.sub(r"^/*", "", path)
        try:
            att: SharedFile = self.conn.getAttributes(
                self.shared_folder_name,
                path
            )
        except:
            print(f"[ ERROR ] {self.shared_folder_name}:{path} does'n exist in NAS.")
            return None
        
        dirs = list()
        files = list()
        if att.isDirectory:
            self.synchronize(path)
            items: List[SharedFile] = self.conn.listPath(self.shared_folder_name, path)
            for item in items:
                if item.isDirectory:
                    dirs.append(item.filename)
                else:
                    files.append(item.filename)
        return (dirs, files)


    # This function synchronizes a file or directory located at "path" with nas.
    # If path specifies a directory, synchronization is done recursively.
    def synchronize(self, path: str) -> bool:
        path = re.sub(r"^/*", "", path)
        local_path = self.tmp_dir_path + path
        try:
            att: SharedFile = self.conn.getAttributes(
                self.shared_folder_name,
                path
            )
        except:
            print(f"[ ERROR ] {self.shared_folder_name}:{path} doesn't exist in NAS.")
            return False
        
        if att.isDirectory:
            if not os.path.exists(local_path):
                os.mkdir(local_path)
            for catt in self.conn.listPath(self.shared_folder_name, path):
                if catt.filename == "." or catt.filename == ".." or catt.filename == "#recycle":
                    continue
                self.synchronize(path + "/" + catt.filename)
            return True
        
        # file
        if path not in self.nas_data or \
           self.nas_data[path].last_write_time != att.last_write_time:
            with open(local_path, "wb") as file:
                print(f"[ INFO ] Pull a file {path} from NAS.")
                self.conn.retrieveFile(
                    self.shared_folder_name,
                    path,
                    file
                )
                self.nas_data[path] = att
        return True


    def get_file(self, file_path: str) -> Union[None, bytes]:
        local_file_path = "./" + self.tmp_dir_path + file_path
        if self.synchronize(file_path):
            with open(local_file_path, "rb") as file:
                return file.read()
        return None
