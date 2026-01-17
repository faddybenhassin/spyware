# Browser Credential Extractor

A Python utility for extracting and decrypting saved passwords from Chrome and Edge browsers on Windows systems.

## Overview

This project consists of two modules:

1. **main.py** - Extracts encrypted master keys and login databases from Chrome and Edge
2. **decrypt.py** - Decrypts the extracted passwords using AES-256-GCM decryption

## How It Works

### Master Key Extraction (main.py)

The Chrome and Edge browsers store a master encryption key in their Local State configuration file located at:
- Chrome: `AppData\Local\Google\Chrome\User Data\Local State`
- Edge: `AppData\Local\Microsoft\Edge\User Data\Local State`

This master key is encrypted using Windows Data Protection API (DPAPI). The script:
1. Reads the Local State JSON file
2. Extracts the base64-encoded encrypted master key
3. Decrypts it using Windows DPAPI (`CryptUnprotectData`)
4. Saves the decrypted master key for use in password decryption

### Database Extraction (main.py)

Login credentials are stored in SQLite databases:
- Chrome: `AppData\Local\Google\Chrome\User Data\default\Login Data`
- Edge: `AppData\Local\Microsoft\Edge\User Data\default\Login Data`

The script copies these databases to a local directory for processing.

### Password Decryption (decrypt.py)

Chromium browsers (Chrome, Edge) use AES-256-GCM encryption for storing passwords. The decryption process:
1. Reads the encrypted password from the SQLite database
2. Extracts the nonce (initialization vector) and authentication tag from the encrypted data
3. Uses the master key to decrypt the password with AES-256-GCM
4. Verifies the authentication tag for data integrity
5. Exports decrypted credentials to CSV files

## Requirements

- Python 3.x
- Windows operating system
- `pywin32` library (for DPAPI decryption)
- `cryptography` library (for AES-256-GCM decryption)

Install dependencies:
```bash
pip install pywin32 cryptography
```

## File Structure

```
├── main.py          # Master key and database extraction
├── decrypt.py       # Password decryption logic
└── README.md        # This file
```

## Usage

### Step 1: Extract Keys and Databases

Run the extraction script to extract the master keys and login databases:
```bash
python main.py
```

This creates a hidden directory (named after your Windows username) containing:
- `ChromeKey.dat` - Chrome's decrypted master key
- `ChromeData.db` - Chrome's login database
- `EdgeKey.dat` - Edge's decrypted master key
- `EdgeData.db` - Edge's login database

### Step 2: Decrypt Passwords

Run the decryption script to decrypt the passwords:
```bash
python decrypt.py
```

This generates two CSV files:
- `Chrome.csv` - Decrypted Chrome passwords with columns: URL, userName, pwd
- `Edge.csv` - Decrypted Edge passwords with columns: URL, userName, pwd

## Output Format

The CSV files contain the following columns:
| URL | userName | pwd |
|-----|----------|-----|
| https://example.com | user@example.com | password123 |

## Technical Details

### AES-256-GCM Encryption Format

Chromium browsers store encrypted passwords in the following format:
```
[3-byte header (v10)] + [12-byte nonce] + [encrypted data] + [16-byte auth tag]
```

- **Header**: Version identifier ("v10")
- **Nonce**: Initialization vector for GCM mode
- **Encrypted Data**: The actual password encrypted with AES-256
- **Auth Tag**: Ensures data integrity and authenticity

### Windows DPAPI

The master key stored in Local State is encrypted using Windows DPAPI (Data Protection API), which uses the user's Windows login credentials as the basis for encryption. Only the logged-in user can decrypt this key.

## Limitations

- Requires the script to run as the same user who owns the browser data
- Only works on Windows systems (due to DPAPI dependency)
- Requires read access to browser files (usually only possible when browser is closed)
- Doesn't work if the user has set a sync passphrase in Chrome/Edge

## Notes

- The directory created contains sensitive data and is hidden from normal file explorer view
- Decrypted passwords should be handled with appropriate security measures
- This tool should only be used on systems where you have proper authorization

## License

Educational purposes only.
