from flask import Flask
import platform
from smb.SMBConnection import SMBConnection
from smb.base import SharedFile
import io
import os




class NAS:
    def __init__(self, uname: str, passwd: str, server_ip: str, server_port: int, 
                 shared_folder_name: str, tmp_dir_path: str):
        self.uname                  = uname
        self.passwd                 = passwd
        self.server_ip              = server_ip
        self.server_port            = server_port
        self.shared_folder_name     = shared_folder_name
        self.tmp_dir_path           = tmp_dir_path
        self.conn: SMBConnection    = None
        self.dir_tree               = dict()

        self.connect()
        self.check()
        self.synchronize("/")
        print("Synchronization with NAS is completed.")


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
        except:
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

    
    def ls(self, dir_path: str):
        try:
            items = self.conn.listPath(self.shared_folder_name, dir_path)
            print(items)
            res = ""
            for item in items:
                res += item.filename
                res += "\r\n"
            return res
        except:
            return None


    def synchronize(self, dir_path: str):
        local_dir_path = "./" + self.tmp_dir_path + dir_path
        if not os.path.exists(local_dir_path):
            os.mkdir(local_dir_path)

        dir_lst: list[SharedFile] = self.conn.listPath(self.shared_folder_name, dir_path)
        for data in dir_lst:
            if data.filename == "." or data.filename == ".." or data.filename == "#recycle":
                continue
            if (data.isDirectory):
                self.synchronize(dir_path + data.filename + "/")
            else:
                with open(local_dir_path + data.filename, "wb") as file:
                    self.conn.retrieveFile(
                        self.shared_folder_name,
                        dir_path + data.filename,
                        file
                    )

