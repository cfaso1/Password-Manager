# Password Manager

## Usage

### Install

- Right click `PasswordManager-Windows.zip` file
- Select `Extract all`
- Select destination to extract to
    - This will be where the passwords and app is stored
    - Choose a location that will not be deleted
- Open the extracted folder
- The `PasswordManager.exe` is the application

### Add to desktop

- Right click `PasswordManager.exe`
- Windows 11 - Click `Show more options` at bottom
- \> Send to \> Desktop (create shortcut)

### Data Backup

- The database folder is stored next to the app in the `database` folder
- To backup the passwords, copy this folder and store it elsewhere
- To import the backed up passwords, paste the database folder back here
    - This will over ride the current master password and saved passwords

### Master Password Reset

- **There is no master password recovery**
- **Changing the master password will delete all saved passwords**
- If master password is forgotten or wants to be changed
    - Delete the `database` folder next to the application
    - Again, this will delete all saved passwords
    - This will reset the database and create a new one
