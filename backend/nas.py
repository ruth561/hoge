from flask import Flask
import platform
from smb.SMBConnection import SMBConnection
from smb.base import SharedFile, OperationFailure
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
        self.tmp_dir_path           = tmp_dir_path + "/"
        self.conn: SMBConnection    = None
        self.nas_data: dict[str, SharedFile]    = dict()

        self.connect()
        self.check()
        self.synchronize("")
        print("Synchronization with NAS is completed.")

        print(self.get_file("/README.md"))
        print(self.get_file("/README.md"))
        print(self.get_file("/README.md"))


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


    # This function synchronizes a file or directory located at "path" with nas.
    # If path specifies a directory, synchronization is done recursively.
    def synchronize(self, path: str) -> bool:
        local_path = "./" + self.tmp_dir_path + path
        try:
            att: SharedFile = self.conn.getAttributes(
                self.shared_folder_name,
                path
            )
        except:
            print(f"[ ERROR ] {self.shared_folder_name}:{path} does'n exist in NAS.")
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


    def get_file(self, file_path: str) -> bytes:
        local_file_path = "./" + self.tmp_dir_path + file_path
        if self.synchronize(file_path):
            with open(local_file_path, "rb") as file:
                return file.read()
        return "Nothing"
