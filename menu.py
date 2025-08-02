import tkinter as tk # GUI
import pyperclip, platform # To copy to clipboard
import password_checker # Password strength
import random, string # Random password

# Swap frams
def show_frame(frame):
    frame.tkraise()

# Color password field based on password strength
def color_password(entry, *args):
    pwd = entry.get()
    strength = password_checker.pwd_strength(pwd)
    if len(pwd)==0:
        entry.config(bg="white")
    elif strength == "Strong":
        entry.config(bg="lightgreen")
    elif strength == "Moderate":
        entry.config(bg="yellow")
    else:
        entry.config(bg="red")

# Create main app window
root = tk.Tk()
root.title("Password Manager")
root.geometry("300x200")
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)
root.resizable(False, False)


# Frame 1: Login Screen 
class LoginScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(bg="lightblue")

        # Master label and entry
        tk.Label(self, text="Enter Master Password:", font=("Arial", 14), bg="lightblue").pack(pady=10)
        self.master_pwd = tk.Entry(self, show='*')
        self.master_pwd.pack(pady=5)
        self.login_btn = tk.Button(self, text="Login", command=self.login)
        self.login_btn.pack(pady=5)
        tk.Button(self, text=" Quit ", command=root.destroy).pack(pady=10)

    # Check password and go to home screen if correct
    def login(self):
        if self.master_pwd.get() == "test":
            show_frame(home)
        else:
            self.login_btn.config(text="Try Again")


# Frame 2: Home 
class HomeScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(bg="lightblue")

        # Welcome title
        self.title = tk.Label(self, text="Welcome!", font=("Arial", 14), bg="lightblue")
        self.title.pack(pady=10)

        # Home Buttons
        tk.Button(self, text="New Password", command=lambda: show_frame(insertion), width=10).pack(pady=10)
        tk.Button(self, text="Find Password", command=lambda: show_frame(search), width=10).pack(pady=10)
        tk.Button(self, text="Quit App", command=root.destroy, width=10).pack(pady=10)


# Frame 3: Insertion
class InsertionScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(bg="lightblue")
        self.grid()

        # Website label and entry
        tk.Label(self, text = "Website: ", bg="lightblue", font=("Arial", 12), pady=10, padx=5).grid(row=1, column=0)
        self.website = tk.Entry(self)
        self.website.grid(row=1, column=1)

        # Username label and entry
        tk.Label(self, text="Username: ", bg="lightblue", font=("Arial", 12), pady=10, padx=5).grid(row=2, column=0)
        self.username = tk.Entry(self)
        self.username.grid(row=2, column=1)

        # Password label and entry with auto strength check
        tk.Label(self, text="Password: ", bg="lightblue", font=("Arial", 12), pady=10, padx=5).grid(row=3, column=0)
        self.password = tk.Entry(self)
        self.password.grid(row=3, column=1)
        self.password.bind("<KeyRelease>", lambda event: color_password(self.password))

        # Feedback Button
        self.feedback_btn = tk.Button(self, text="Feedback", command=self.feedback_func, pady=5, width=10)
        self.feedback_btn.grid(row=4, column=1)

        # Add password button
        self.insert_btn = tk.Button(self, text="Add Password", command=self.insert, width=10)
        self.insert_btn.grid(row=0, column=1)

        # Home button
        tk.Button(self, text="Home", command=lambda: show_frame(home)).grid(row=0, column=0)

        # Random password button
        self.random_btn = tk.Button(self, text="Generate", command=self.generate_password, pady=5, width=5)
        self.random_btn.grid(row=4, column=0)
    
    # Feedback button functions
    def feedback_func(self):
        feedback.set_password()
        feedback.set_feedback()
        show_frame(feedback)

    # Generate password and show in password field
    def generate_password(self):
        LENGTH = 15
        characters = string.ascii_letters + string.digits + string.punctuation
        random_password = ''.join(random.choice(characters) for _ in range(LENGTH))

        self.password.delete(0, tk.END)
        self.password.insert(0, random_password)
        color_password(self.password)

        pyperclip.copy(random_password)
        self.random_btn.config(text="Copied")

    # Data base insertion if fields filled in
    def insert(self):
        # Reset field color
        self.website.config(bg="white")
        self.username.config(bg="white")
        color_password(self.password)

        if self.website.get() and self.username.get() and self.password.get():
            # TODO make real database
            data = {self.website.get(): {"username": self.username.get(), "password": self.password.get()}}
            database.update(data)
            
            home.title.config(text="Password Added!")
            self.insert_btn.config(text="Add Password")
            show_frame(home)

            # Reset field text
            self.website.delete(0, tk.END)
            self.username.delete(0, tk.END)
            self.password.delete(0, tk.END)
            self.password.config(bg="white")
            self.random_btn.config(text="Generate")
        else:
            # Change colors of fileds not filled in
            if not self.website.get():
                self.website.config(bg="lightcoral")
            if not self.username.get():
                self.username.config(bg="lightcoral")
            if not self.password.get():
                self.password.config(bg="lightcoral")
            self.insert_btn.config(text="Try Again")


# Frame 4: Feedback
class FeedbackScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(bg="lightblue")
        self.grid()

        # Title
        tk.Label(self, text="Password Feedback", font=("Arial", 14), bg="lightblue", width=30).grid(row=0, column=0, columnspan=2)

        # Password Entry
        self.password = tk.Entry(self, width=20)
        self.password.grid(row=1, column=0)
        self.password.bind("<KeyRelease>", lambda event: (color_password(self.password), self.set_feedback()))

        # Feedback
        self.feedback = tk.Label(self, font=("Arial", 11), bg="lightblue", wraplength=300, justify="left")
        self.feedback.grid(row=2, column=0, columnspan=2)

        # Return Button
        tk.Button(self, text="Back", command=lambda: self.exit_feedback(), padx=10).grid(row=1, column=1)

    # Initial password text and color
    def set_password(self):
        self.password.insert(0, insertion.password.get())
        color_password(self.password)

    # Set feedback
    def set_feedback(self):
        pwd = self.password.get()
        if pwd:
            feedback = password_checker.pwd_feedback(pwd)
            strength = password_checker.pwd_strength(pwd)
            score = password_checker.pwd_score(pwd)
            if score >= 100:
                score = "100+"
            output = f"Strength: {strength}    Score: {score}\n{feedback}"
            self.feedback.config(text=output)
        else:
            self.feedback.config(text="")

    # Exit feedback and update fields
    def exit_feedback(self):
        insertion.password.delete(0, tk.END)
        insertion.password.insert(0, self.password.get())
        color_password(insertion.password)
        self.password.delete(0, tk.END)
        show_frame(insertion)
        

# Frame 5: Search
class SearchScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(bg="lightblue")

        # Title
        tk.Label(self, text="Search For Password", font=("Arial", 14), bg="lightblue").pack(pady=10)

        # Label, Entry, Button
        self.title = tk.Label(self, text="Enter Website:", font=("Arial", 12), bg="lightblue")
        self.title.pack(pady=5)
        self.website = tk.Entry(self)
        self.website.pack(pady=5)
        tk.Button(self, text="Search", command=lambda: self.find_website()).pack(pady=5)
        tk.Button(self, text="Home", command=lambda: show_frame(home)).pack(pady=5)

    # Querey database
    def find_website(self):
        if self.website.get()=="test": # is in database
            view = ViewScreen(root)
            view.grid(row=0, column=0, sticky="nsew")
            show_frame(view)
        else:
            self.title.config(text="Invalid Website:")


# Frame 6: View
class ViewScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(bg="lightblue")
        self.grid()

        # Data
        website = search.website.get() 
        username = "test" # Get from db 
        password = "test" # Get from db

        if len(website) > 20:
            dsp_web = website
        else:
            dsp_web = website
        if len(username) > 20:
            dsp_usr = username
        else:
            dsp_usr = username
        if len(password) > 20:
            dsp_pwd = password
        else:
            dsp_pwd = password

        # Labels 
        tk.Label(self, text=f"Website: {dsp_web}", font=("Arial", 14), bg="lightblue", justify="left").grid(row=0, column=0)
        tk.Label(self, text=f"Username: {dsp_usr}", font=("Arial", 14), bg="lightblue", justify="left", wraplength=250).grid(row=1, column=0)
        tk.Label(self, text=f"Password: {dsp_pwd}", font=("Arial", 14), bg="lightblue", justify="left", wraplength=200).grid(row=2, column=0)

        web_btn = tk.Button(self, text="Copy", command=lambda: (pyperclip.copy(website), web_btn.config(text="Copied")), width=5)
        web_btn.grid(row=0, column=1)
        usr_btn = tk.Button(self, text="Copy", command=lambda: (pyperclip.copy(username), usr_btn.config(text="Copied")), width=5)
        usr_btn.grid(row=1, column=1)
        pwd_btn = tk.Button(self, text="Copy", command=lambda: (pyperclip.copy(password), pwd_btn.config(text="Copied")), width=5)
        pwd_btn.grid(row=2, column=1)
        
        tk.Button(self, text="Back", command=lambda: show_frame(search)).grid(row=3, column=0)

# Initialize
login = LoginScreen(root)
home = HomeScreen(root)
insertion = InsertionScreen(root)
feedback = FeedbackScreen(root)
search = SearchScreen(root)
database = {}

# Stack frames
for frame in (login, home, insertion, feedback, search):
    frame.grid(row=0, column=0, sticky="nsew")

# Copy to clipboard compatability
os_name = platform.system()
if os_name == "Linux":
    pyperclip.set_clipboard("xclip")
elif os_name == "Windows":
    pyperclip.set_clipboard("windows")
else:
    raise RuntimeError(f"Unsupported OS: {os_name}")


# Begin
show_frame(login)
root.mainloop()
