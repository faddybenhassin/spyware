import sqlite3
import csv
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


def decrypt_password(encrypted_password, master_key):
    try:
        # Extract the nonce, ciphertext, and authentication tag
        nonce = encrypted_password[3:15]  # Extract the nonce from the encrypted data
        encrypted_data = encrypted_password[15:-16]  # Extract the encrypted data (excluding the tag)
        tag = encrypted_password[-16:]  # The last 16 bytes are the authentication tag
        
        # Set up the cipher for decryption
        cipher = Cipher(
            algorithms.AES(master_key),
            modes.GCM(nonce, tag),
            backend=default_backend()
        )
        
        # Perform decryption
        decryptor = cipher.decryptor()
        decrypted_password = decryptor.update(encrypted_data) + decryptor.finalize()
        
        return decrypted_password.decode('utf-8')
    except:
        return None
    
    
def decrypt(data,key,output):
    master_key = open(key, "rb").read()
    con = sqlite3.connect(data)
    cur = con.cursor()
    cur.execute("SELECT signon_realm, username_value, password_value FROM 'logins'")
            
    with open (output , 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["URL", "userName", "pwd"])
        for r in cur.fetchall():
            url = r[0]
            username = r[1]
            encrypted_password = r[2]
            pwd = decrypt_password(encrypted_password, master_key)
            if pwd:
                writer.writerow([url, username, pwd])
    if con:
        con.close()
                
        
if __name__ == "__main__":
    decrypt("ChromeData.db","ChromeKey.dat","Chrome.csv")
    decrypt("EdgeData.db","EdgeKey.dat","Edge.csv")