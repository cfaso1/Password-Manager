import tkinter as tk # GUI
import tkinter.font as tkfont # Fonts
import pyperclip, platform # Copying to clipboard
import random, string # Random password generation
import password_checker # Password strength check
import database, crypto, os # Database and data encryption
from pathlib import Path # Database folder creation

# Clipboard setup
os_name = platform.system()
if os_name == "Linux":
    pyperclip.set_clipboard("xclip")
elif os_name == "Windows":
    pyperclip.set_clipboard("windows")
elif os_name == "Darwin":  
    pyperclip.set_clipboard("pbcopy")
else:
    raise RuntimeError(f"Unsupported OS: {os_name}")

# Central App class to control all screens
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Password Manager")
        self.geometry("300x200")
        self.resizable(False, False)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Dictionary to store all screen instances
        self.frames = {}

        # Initialize database
        self.salt = None
        self.db_conn = None
        self.encryption_key = None

        # Create database directory
        script_dir = Path(__file__).resolve().parent
        parent_dir = script_dir.parent
        self.db_folder = parent_dir / "database"
        self.db_folder.mkdir(parents=True, exist_ok=True)

        # Check if database exists
        if not os.path.exists(self.db_folder / "vault.db"): 
            self.show_frame(InitialScreen)
        else:
            self.show_frame(LoginScreen) 
            self.salt = crypto.load_or_create_salt(self.db_folder)
            self.db_conn = database.init_db(self.db_folder)

    # Used to swtich frames
    def show_frame(self, screen_class):
        # Create frame if it doesn't exist yet
        if screen_class not in self.frames:
            frame = screen_class(self)
            self.frames[screen_class] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.frames[screen_class].tkraise()

    # Get frame class of given screen
    def get_frame(self, screen_class):
        return self.frames.get(screen_class)
    
    # Utility to color password entry
    def color_password(self, entry):
        pwd = entry.get()
        strength = password_checker.pwd_strength(pwd)
        if not pwd:
            entry.config(bg="white")
        elif strength == "Strong":
            entry.config(bg="lightgreen")
        elif strength == "Moderate":
            entry.config(bg="yellow")
        else:
            entry.config(bg="red")

    # Initialize master password
    def set_master_password(self, password):
        self.salt = crypto.load_or_create_salt(self.db_folder)
        self.db_conn = database.init_db(self.db_folder)
        self.encryption_key = crypto.derive_key(password, self.salt)
        database.store_check_value(self.db_conn, self.encryption_key)

    # Close app and remove key
    def quit(self):
        self.encryption_key = None
        self.destroy()


# Frame: Initial
class InitialScreen(tk.Frame):
    def __init__(self, app):
        super().__init__(app, bg="lightblue")
        self.app = app

        # Title
        tk.Label(self, text="Welcome to Password Manager!", font=("Arial", 14, "bold"), bg="lightblue").pack(pady=5)

        # Info
        info = tk.Text(self, bg="lightblue", font=("Arial", 12), height=5)
        info.pack(pady=5)
        info.tag_configure("bold", font=("Arial", 12, "bold"))
        info.insert("1.0", "Please note the following:\n" \
        "- All data is stored locally\n" \
        "- All passwords are encrypted\n" \
        "- No data is backed up\n" \
        "- No master password recovery\n")
        info.tag_add("bold", "5.0", tk.END)
        info.config(state="disabled")

        # Button
        tk.Button(self, text="Acknowledge", command=self.acknowledge).pack(pady=5)

    # Switch screens
    def acknowledge(self):
        self.app.show_frame(SetupScreen)
        self.app.frames[InitialScreen].destroy()
        del self.app.frames[InitialScreen]


# Frame: Setup
class SetupScreen(tk.Frame):
    def __init__(self, app):
        super().__init__(app, bg="lightblue")
        self.app = app

        # Title and entry 1
        tk.Label(self, text="Create Master Password", font=("Araial", 14, "bold"), bg="lightblue").pack(pady=2)
        self.pwd1 = tk.Entry(self)
        self.pwd1.pack(pady=2)
        self.pwd1.bind("<KeyRelease>", lambda event: self.app.color_password(self.pwd1))

        # Title and entry 2
        tk.Label(self, text="Confirm Password", font=("Araial", 14), bg="lightblue").pack(pady=2)
        self.pwd2 = tk.Entry(self)
        self.pwd2.pack(pady=2)

        # Buttons
        self.set_btn = tk.Button(self, text="Set Password", command=self.check_pwd, width=10)
        self.set_btn.pack(pady=2)
        self.feedback_btn = tk.Button(self, text="Feedback", command=self.to_feedback, width=10)
        self.feedback_btn.pack(pady=2)

    # Confirm passwords match and recolor if not
    def check_pwd(self):
        self.pwd1.config(bg="white")
        self.pwd2.config(bg="white")
        if self.pwd1.get() and self.pwd1.get() == self.pwd2.get():
           self.confirm()
           return True
        else:
            self.set_btn.config(text="Try Again")
            self.pwd1.config(bg="lightcoral")
            self.pwd2.config(bg="lightcoral")
            return False

    # User conformation to set master password
    def confirm(self):
        self.pwd1.config(bg="lightgreen")
        self.pwd2.config(bg="lightgreen")
        self.set_btn.config(text="Confirm")
        self.set_btn.config(command=self.set_master)

    # Initialize master password and show login if passwords match
    def set_master(self):
        if self.check_pwd():
            self.app.set_master_password(self.pwd1.get())
            self.app.show_frame(LoginScreen)
            self.app.frames[SetupScreen].destroy()
            del self.app.frames[SetupScreen]
        else:
            self.set_btn.config(command=self.check_pwd)

    # Change to Feedback screen
    def to_feedback(self):
        self.app.show_frame(FeedbackScreen)
        feedback_screen = self.app.get_frame(FeedbackScreen)
        feedback_screen.back_btn.config(command=lambda: feedback_screen.back(SetupScreen, self.pwd1))
        feedback_screen.set_password(self.pwd1.get())


# Frame: Login
class LoginScreen(tk.Frame):
    def __init__(self, app):
        super().__init__(app, bg="lightblue")
        self.app = app

        # Title and entry
        tk.Label(self, text="Enter Master Password:", font=("Arial", 14, "bold"), bg="lightblue").pack(pady=5)
        self.master_pwd = tk.Entry(self, show='*', font=("Arial", 12))
        self.master_pwd.pack(pady=5)

        # Login and quit buttons
        self.login_btn = tk.Button(self, text="Login", command=self.login, width=9)
        self.login_btn.pack(pady=5)
        tk.Button(self, text="Quit", command=lambda: self.app.quit(), width=9).pack(pady=5)

        # Throttling
        self.throttle = tk.Label(self, bg="lightblue")
        self.throttle.pack(pady=5)
        self.failed_count = 0

    # Check master password and login
    def login(self):
        valid, key = self.verify_master_password(self.master_pwd.get(), self.app.salt, self.app.db_conn)
        self.app.encryption_key = key
        if valid:          
            self.app.show_frame(HomeScreen)
            self.app.get_frame(LoginScreen).destroy()
            del self.app.frames[LoginScreen]
        else:
            self.login_btn.config(text="Try Again")
            self.master_pwd.delete(0, tk.END)
            self.failed_count += 1
            if self.failed_count > 2:
                self.delay()
        
    # Verify master password
    def verify_master_password(self, input_password, salt, conn):
        key = crypto.derive_key(input_password, salt)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT check_value FROM meta")
            encrypted_check = cursor.fetchone()[0]
            return (crypto.decrypt(encrypted_check, key) == "vault_check"), key
        except:
            return False, None
    
    # Password throttling
    def delay(self):
        MAX_DELAY = 120 # Seconds
        delay = min(2**(self.failed_count - 2), MAX_DELAY)
        self.throttle.config(text=f"Too many attempts.\n wait {delay} seconds")
        self.login_btn.config(state="disabled")
        self.after(delay * 1000, self.throttle_reset)
    
    def throttle_reset(self):
        self.throttle.config(text="")
        self.login_btn.config(state="normal")


# Frame: Home
class HomeScreen(tk.Frame):
    def __init__(self, app):
        super().__init__(app, bg="lightblue")
        self.app = app

        # Title
        self.title = tk.Label(self, text="Welcome!", font=("Arial", 14, "bold"), bg="lightblue")
        self.title.pack(pady=8)

        # Buttons
        tk.Button(self, text="New Password", command=lambda: app.show_frame(InsertionScreen), width=12).pack(pady=8)
        tk.Button(self, text="Find Password", command=lambda: app.show_frame(SearchScreen), width=12).pack(pady=8)
        tk.Button(self, text="Quit App", command=lambda: self.app.quit(), width=12).pack(pady=8)


# Frame: Insertion
class InsertionScreen(tk.Frame):
    def __init__(self, app):
        super().__init__(app, bg="lightblue")
        self.app = app

        # Form titles and entries
        tk.Label(self, text="Website:", bg="lightblue", font=("Arial", 14)).grid(row=0, column=0, pady=5, padx=5)
        self.website = tk.Entry(self, font=("Arial", 10))
        self.website.grid(row=0, column=1)

        tk.Label(self, text="Username:", bg="lightblue", font=("Arial", 14)).grid(row=1, column=0, pady=5, padx=5)
        self.username = tk.Entry(self, font=("Arial", 10))
        self.username.grid(row=1, column=1)

        tk.Label(self, text="Password:", bg="lightblue", font=("Arial", 14)).grid(row=2, column=0, pady=5, padx=5)
        self.password = tk.Entry(self, font=("Arial", 10))
        self.password.grid(row=2, column=1)
        self.password.bind("<KeyRelease>", lambda event: self.app.color_password(self.password))

        # Buttons
        self.insert_btn = tk.Button(self, text="Add Password", command=self.insert, width=12)
        self.insert_btn.grid(row=4, column=1, pady=5)

        tk.Button(self, text="Home", command=self.to_home, width=7).grid(row=4, column=0)

        self.random_btn = tk.Button(self, text="Generate", width=7, command=self.generate_password)
        self.random_btn.grid(row=3, column=0, pady=5)

        tk.Button(self, text="Feedback", command=self.to_feedback, width=12).grid(row=3, column=1, pady=5)

    # Confirm all fields are filled in then update database
    def insert(self):
        self.website.config(bg="white")
        self.username.config(bg="white")
        self.app.color_password(self.password)

        # Add new database entry if fields are filled in
        website, username, password = self.website.get(), self.username.get(), self.password.get()
        if website and username and password:
            database.add_entry(self.app.db_conn, website, username, password, self.app.encryption_key)
            self.to_home()
            app.get_frame(HomeScreen).title.config(text="Password Added!")
        else:
            # Fields not filled in are set to lightcoral color
            if not website: self.website.config(bg="lightcoral")
            if not username: self.username.config(bg="lightcoral")
            if not password: self.password.config(bg="lightcoral")
            self.insert_btn.config(text="Try Again")

    # Generate random 15 digit long password of random characters
    def generate_password(self):
        LENGTH = 15
        chars = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choice(chars) for _ in range(LENGTH))
        self.password.delete(0, tk.END)
        self.password.insert(0, password)
        self.app.color_password(self.password)
        pyperclip.copy(password)
        self.random_btn.config(text="Copied")

    # Return to homee screen
    def to_home(self):
        self.app.show_frame(HomeScreen)
        self.app.get_frame(HomeScreen).title.config(text="Home")
        self.app.frames[InsertionScreen].destroy()
        del self.app.frames[InsertionScreen]

    # To Feedback screen
    def to_feedback(self):
        self.app.show_frame(FeedbackScreen)
        self.app.get_frame(FeedbackScreen).set_password(self.password.get())


# Frame: Feedback
class FeedbackScreen(tk.Frame):
    def __init__(self, app):
        super().__init__(app, bg="lightblue")
        self.app = app

        # Title
        tk.Label(self, text="Password Feedback", font=("Arial", 14, "bold"), bg="lightblue", width=30).grid(row=0, column=0, columnspan=2)

        # Entry
        self.password = tk.Entry(self, font=("Arial", 10))
        self.password.grid(row=1, column=0)
        self.password.delete(0, tk.END)
        self.password.bind("<KeyRelease>", lambda e: (self.app.color_password(self.password), self.set_feedback()))

        # Feedback
        self.feedback = tk.Text(self, bg="lightblue", font=("Arial", 12), width=32, wrap="word", state="disabled")
        self.feedback.grid(row=2, column=0, sticky="nsw", columnspan=2)
        self.feedback.tag_configure("center", justify="center")

        # Scrollbar
        scrollbar =  tk.Scrollbar(self, orient="vertical", command=self.feedback.yview)
        scrollbar.grid(row=2, column=1, sticky="nse")
        self.feedback.config(yscrollcommand=scrollbar.set)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Back Button
        self.back_btn = tk.Button(self, text="Back", command=lambda: self.back(InsertionScreen, self.app.get_frame(InsertionScreen).password))
        self.back_btn.grid(row=1, column=1)

    # Set password in feedback
    def set_password(self, pwd):
        self.password.insert(0, pwd)
        self.app.color_password(self.password)
        self.set_feedback()

    # Generate the feedback using password_checker.py
    def set_feedback(self):
        pwd = self.password.get()
        self.feedback.config(state="normal")
        if pwd:
            feedback = password_checker.pwd_feedback(pwd)
            strength = password_checker.pwd_strength(pwd)
            score = min(password_checker.pwd_score(pwd), 100)
            self.feedback.delete("1.0", tk.END)
            self.feedback.insert("1.0", f"Strength: {strength}    Score: {score}\n{feedback}")
            self.feedback.tag_add("center", "1.0", "end")
        else:
            self.feedback.delete("1.0", tk.END)
        self.feedback.config(state="disabled")

    # Given screen to return to and field to modify
    def back(self, screen, field):
        field.delete(0, tk.END)
        field.insert(0, self.password.get())
        self.app.color_password(field)
        self.app.show_frame(screen)
        self.app.frames[FeedbackScreen].destroy()
        del self.app.frames[FeedbackScreen]


# Frame: Search
class SearchScreen(tk.Frame):
    def __init__(self, app):
        super().__init__(app, bg="lightblue")
        self.app = app

        # Titles
        tk.Label(self, text="Search For Password", font=("Arial", 14, "bold"), bg="lightblue").pack(pady=2)
        self.web_title = tk.Label(self, text="Enter Website:", font=("Arial", 12), bg="lightblue")
        self.web_title.pack(pady=2)

        # Entry
        self.website = tk.Entry(self, font=("Arial", 10))
        self.website.pack(pady=2)

        # Buttons
        self.btn = tk.Button(self, text="Search", command=self.search, width=7)
        self.btn.pack(pady=2)
        tk.Button(self, text="Show All", command=lambda: self.app.show_frame(AllScreen), width=7).pack(pady=2)
        tk.Button(self, text="Home", command=self.to_home, width=7).pack(pady=2)

    # Query database and set to View screen
    def search(self):
        website, username, password = database.get_entry(self.app.db_conn, self.website.get(), self.app.encryption_key)
        if  website:  
            self.app.show_frame(ViewScreen)
            self.app.get_frame(ViewScreen).set_fields(website, username, password)
            self.app.frames[SearchScreen].destroy()
            del self.app.frames[SearchScreen]
        else:
            self.btn.config(text="Try Again")
            self.web_title.config(text="Invalid Website:")

    # Return to Home screen
    def to_home(self):
        self.app.get_frame(HomeScreen).title.config(text="Home")
        self.app.show_frame(HomeScreen)
        self.app.frames[SearchScreen].destroy()
        del self.app.frames[SearchScreen]


# Frame: View
class ViewScreen(tk.Frame):
    def __init__(self, app):
        super().__init__(app, bg="lightblue")
        self.app = app

        # Initialize data
        self.website = None
        self.username = None
        self.password = None

        # Data Titles
        self.web_data = tk.Label(self, bg="lightblue", font=("Arial", 14, "bold"), width=25)
        self.web_data.grid(row=0, column=0, columnspan=2)
        self.usr_data = tk.Label(self, bg="lightblue", font=("Arial", 14), width=25)
        self.usr_data.grid(row=1, column=0, columnspan=2)
        self.pwd_data = tk.Label(self, bg="lightblue", font=("Arial", 14), width=25)
        self.pwd_data.grid(row=2, column=0, columnspan=2)

        # Copy Buttons
        self.usr_cpy = tk.Button(self, text="Copy Username", command=self.usr_copy, width=13)
        self.usr_cpy.grid(row=3, column=0, pady=5)
        self.pwd_cpy = tk.Button(self, text="Copy Password", command=self.pwd_copy, width=13)
        self.pwd_cpy.grid(row=3, column=1, pady=5)

        # Edit Buttons
        tk.Button(self, text="Edit Username", command=lambda: self.edit_field("Username", self.username), width=13).grid(row=4, column=0, pady=5)
        tk.Button(self, text="Edit Password", command=lambda: self.edit_field("Password", self.password), width=13).grid(row=4, column=1, pady=5)

        # Delete and back buttons
        self.del_btn = tk.Button(self, text="Delete Entry", command=self.confirm_del, width=13)
        self.del_btn.grid(row=5, column=0)
        tk.Button(self, text="Back", command=self.to_search, width=13).grid(row=5, column=1)

    # Set fields
    def set_fields(self, website, username, password):
        self.website, self.username, self.password = website, username, password
        self.web_data.config(text=f"{self.website} Info:") 
        self.usr_data.config(text=self.username) 
        self.pwd_data.config(text=self.password) 

    # Confirm entry deletion 
    def confirm_del(self):
        self.del_btn.config(text="Confirm")
        self.del_btn.config(command=self.del_entry)
    
    # Delete entry from database and return to search
    def del_entry(self):
        conn = self.app.db_conn
        database.delete_entry(conn, self.website)
        self.to_search()
    
    # Copy Functions
    def usr_copy(self):
        pyperclip.copy(self.username)        
        self.usr_cpy.config(text="Copied Username")
    def pwd_copy(self):
        pyperclip.copy(self.password)        
        self.pwd_cpy.config(text="Copied Password")

    # Edit Function
    def edit_field(self, field, content):
        self.app.show_frame(EditScreen)
        edit_frame = self.app.get_frame(EditScreen)
        edit_frame.title.config(text=f"Editing {field}")
        edit_frame.change.insert(0, content)
        edit_frame.get_data(self.website, self.username, self.password)
        edit_frame.changing = field
        if field=="Password":
            edit_frame.set_feedback() 
    
    # Back button function
    def to_search(self):
        self.app.show_frame(SearchScreen)
        self.app.frames[ViewScreen].destroy()
        del self.app.frames[ViewScreen]


# Frame: Edit
class EditScreen(tk.Frame):
    def __init__(self, app):
        super().__init__(app, bg="lightblue")
        self.app=app

        # Initialize data
        self.website = None
        self.username = None
        self.password = None
        self.changing = None

        # Title
        self.title = tk.Label(self, bg="lightblue", font=("Arial", 14))
        self.title.pack(pady=5)

        # Entry
        self.change = tk.Entry(self, font=("Arial", 10))
        self.change.pack(pady=5)

        # Buttons
        self.edit_btn = tk.Button(self, text="Edit", command=self.confirm_edit, width=7)
        self.edit_btn.pack(pady=5)
        tk.Button(self, text="Cancel", command=self.to_view, width=7).pack(pady=5)

    # Feedback Button if editing password
    def set_feedback(self):
        self.app.color_password(self.change)
        feedback_btn = tk.Button(self, text="Feedback", command=self.to_feedback)
        feedback_btn.pack(pady=5)
        self.change.bind("<KeyRelease>", lambda event: self.app.color_password(self.change))

    # Get data
    def get_data(self, website, username, password):
        self.website = website
        self.username = username
        self.password = password
    
    # Change to Feedback screen
    def to_feedback(self):
        self.app.show_frame(FeedbackScreen)
        feedback_screen = self.app.get_frame(FeedbackScreen)
        feedback_screen.back_btn.config(command=lambda: feedback_screen.back(EditScreen, self.change))
        feedback_screen.set_password(self.change.get())

    # Confirm edit
    def confirm_edit(self):
        self.edit_btn.config(text="Confirm", command=lambda: (self.update_field(), self.to_view()))

    # Update database
    def update_field(self):
        if self.changing == "Username":
            self.username = self.change.get()
        else:
            self.password = self.change.get()
        database.update_entry(self.app.db_conn, self.website, self.username, self.password, self.app.encryption_key)
        self.app.frames[ViewScreen].set_fields(self.website, self.username, self.password)

    # To View Screen
    def to_view(self):
        self.app.show_frame(ViewScreen)
        self.app.frames[EditScreen].destroy()
        del self.app.frames[EditScreen]


# Frame: All
class AllScreen(tk.Frame):
    def __init__(self, app):
        super().__init__(app, bg="lightblue")
        self.app=app

        # Title
        top_frame = tk.Frame(self, bg="lightblue")
        top_frame.pack(fill="x", pady=5)
        tk.Label(top_frame, text="All Saved Websites (A-Z):", font=("Arial", 14, "bold"), bg="lightblue").pack(padx=5, side="left")
        tk.Button(top_frame, text="Back", command=self.back).pack(padx=5, side="right")

        # Text box
        self.text_box = tk.Text(self, wrap="word", font=("Arial", 14), bg="lightblue", width=28, height=10)
        self.text_box.pack(side="left", pady=5) 

        # Scrollbar
        scrollbar = tk.Scrollbar(self, orient="vertical", command=self.text_box.yview)
        scrollbar.pack(side="left", fill="y")
        self.text_box.config(yscrollcommand=scrollbar.set)

        # Get all websites
        websites = database.get_all_entries(self.app.db_conn)
        for i in range (len(websites)):
            self.text_box.insert(tk.END, f"{i+1}. " + websites[i] + "\n")
        self.text_box.config(state="disabled")

    # Return to search
    def back(self):
        self.app.show_frame(SearchScreen)
        self.app.frames[AllScreen].destroy()
        del self.app.frames[AllScreen]


# Start App
if __name__ == "__main__":
    app = App()
    app.mainloop()