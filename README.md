# 🔐 Password Manager

A simple **Password Manager** built with **Python, Tkinter, SQLite3, and Cryptography.**
All data is stored **locally** and protected by a **master password** (cannot be reset).
Includes features like password generation, secure storage, password feedback, and search functionality.

## 📜 Features

- **Secure Authentication**
    - Master password (non-resettable)
    - Password throttling (delays after failed attempts)

- **Password Management**
    - Add new entries (website, username, password)
    - Auto-generate strong passwords
    - Copy passwords to clipboard
    - Search for saved credentials
    - View, edit, or delete entries
    - View all stored passwords at once

- **Security**
    - Passwords encrypted using the cryptography library and a unique salt
    - Password strength feedback via zxcvbn
    - Data stored locally in an SQLite3 database
    - Master password is not stored anywhere

## 🛠️ Tech Stack

- Language: `Python 3`
- Libraries:
    - `tkinter` – GUI
    - `sqlite3` – Database
    - `cryptography` – Encryption
    - `zxcvbn` – Password strength feedback

## ⚠️ Important Notes

- Your **master password cannot be reset.** If lost, all data is unrecoverable.
- All data is stored **locally**; nothing is uploaded to the cloud.
- This project is for **educational purposes only** and not intended for production-level security.

## 📚 Learning Goals
- This project helped me learn:
    - How to use git and GitHub for version control and project sharing
    - How to build a GUI using Tkinter
    - Basics of secure password storage
    - SQLite database integration
    - Handling encryption with salts
    - Implementing UI/UX feedback with password strength indicators

## 🚀 Usage

### Running With Python
**Prerequisite:** Python 3.10+ installed
```bash
# Clone this repository 
$ git clone https://github.com/cfaso1/PasswordManager.git

# Go into the repository
$ cd PasswordManager

# Install dependencies
pip install -r requirements.txt

# Run the app (as module)
python -m app.main
```

### Create App (Optional)
```bash
# Install pyinstaller
$ pip install pyinstaller

# Create app
$ python -m PyInstaller --onedir --windowed --name PasswordManager --icon=app/app.ico app/main.py
```
- This will create a `dist` folder with `_internal` folder and `PasswordManager` app (file type depends on operating system)
- Running this app will launch the program
- To add this app to desktop:
  - Right click > Show more options (Windows 11) > Send to > Desktop (create shortcut)

### Data Backup

- The database folder is stored next to the app in the `database` folder
- To backup the passwords, copy this folder and store it elsewhere
- To import the backed up passwords, paste the database folder back here
    - This will override the current master password and saved passwords

### Master Password Reset

- **There is no master password recovery**
- **Changing the master password will delete all saved passwords**
- If master password is forgotten or wants to be changed:
    - Delete the `database` folder next to the application
    - Again, this will delete all saved passwords
    - This will reset the database and create a new one

### Install from zip (Windows)

- Download given zip folder
- Right click `PasswordManager-Windows.zip` file
- Select `Extract all`
- Select destination to extract to
    - This will be where the passwords and app is stored
    - Choose a location that will not be deleted
- Open the extracted folder
- The `PasswordManager.exe` is the application
- Running this app will launch the program
- To add this app to desktop:
  - Right click > Show more options (Windows 11) > Send to > Desktop (create shortcut)


## 📄 License
MIT License – see LICENSE for details.