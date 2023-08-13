"""Allows users to create an account within the program"""
import tkinter.messagebox
import tkinter
import subprocess
import random
import re
import sys
import customtkinter
import bcrypt

# Sets appearance mode to light and default color theme to dark-blue
customtkinter.set_appearance_mode("light")
customtkinter.set_default_color_theme("dark-blue")

root = customtkinter.CTk()
root.geometry("500x350")
root.title("Signup")


def open_login():
    """Function to open the login.py file and close the signup window"""
    root.destroy()
    subprocess.run(["python", "login.py"])


def generate_user_id():
    """Generates a random userID that will be assigned to every user"""
    user_id = random.randint(1000, 9999)
    with open("DB\\logininfo.txt", "r") as db:
        for line in db:
            if str(user_id) in line:
                return generate_user_id()
    return str(user_id)


def register():
    """Registers a new user"""
    username = entry1.get().lower()
    password1 = entry2.get()
    password2 = entry3.get()

    with open("DB\\logininfo.txt", "r") as db:
        existing_usernames = [line.split(", ")[1].strip().lower() for line in db]

    if len(password1) > 3:
        if " " in username:
            tkinter.messagebox.showerror("Error",
            "Username cannot contain spaces")
            return

        if " " in password1:
            tkinter.messagebox.showerror("Error",
            "Password cannot contain spaces")
            return

        if not re.match("^[a-zA-Z0-9!@#$%^&*()_+{}\[\]:;<>,.?~\\/]+$",
        username):
            tkinter.messagebox.showerror("Error",
            "Username can only contain English letters, "
            "numbers, and characters or is empty")
            return

        if username.lower() in existing_usernames:
            tkinter.messagebox.showerror("Error", "This Username Already " 
            "Exists, Please Enter A Different Username")
            return

        if password1 == password2:
            if not re.match("^[a-zA-Z0-9!@#$%^&*()_+{}\[\]:;<>,.?~\\/]+$", password1):
                tkinter.messagebox.showerror("Error", "Password can only"
                " contain English letters, numbers, and characters")
                return

            password1 = password1.encode('utf-8')
            hashed_password = bcrypt.hashpw(password1, bcrypt.gensalt())

            with open("DB\\logininfo.txt", "a") as db:
                db.write(f"{generate_user_id()}, {username}, {hashed_password}\n")

            tkinter.messagebox.showinfo("Success", 
            "User created successfully!\nPlease login to proceed:")
            root.destroy()  # Close the signup window

            # Run the login.py script using the same Python interpreter
            subprocess.run([sys.executable, "login.py"])

        else:
            tkinter.messagebox.showerror("Error", "Passwords do not match")
            return
    else:
        tkinter.messagebox.showerror("Error", 
        "Password needs to be at least 4 characters long")
        return


def signup():
    register()

# GUI
frame = customtkinter.CTkFrame(master = root)
frame.pack(pady = 20, padx = 60, fill = "both", expand = True)

label = customtkinter.CTkLabel(master = frame,
text = "Create Account", font = ("Blinker", 25))
label.pack(pady = 12, padx = 10)

entry1 = customtkinter.CTkEntry(master = frame,
placeholder_text = "Username")
entry1.pack(padx = 10, pady = 12)

entry2 = customtkinter.CTkEntry(master = frame,
placeholder_text = "Password", show = "*")
entry2.pack(padx = 10, pady = 12)

entry3 = customtkinter.CTkEntry(master = frame,
placeholder_text = "Confirm Password", show = "*")
entry3.pack(padx = 10, pady = 12)

signup_button = customtkinter.CTkButton(master = frame,
text = "Signup", command = signup)
signup_button.pack(pady = 12, padx = 10)

login_label = customtkinter.CTkLabel(master = frame,
text = "Already Have An Account? Click Here!",
font = ("Blinker", 10),cursor = "hand2", fg_color = "#E5E5E5")
login_label.pack(pady = 1)
login_label.bind("<Button-1>", lambda event: open_login())

root.mainloop()
