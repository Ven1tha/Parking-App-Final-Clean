"""Allows users to login with their created account"""
import bcrypt
import customtkinter
import subprocess
import tkinter.messagebox

# Sets the background of the login page to black
customtkinter.set_appearance_mode("light")
# Sets the buttons within the page to blue
customtkinter.set_default_color_theme("dark-blue")

root = customtkinter.CTk()
root.geometry("500x350")
root.title("Login")


def gainAccess():
    """Function to authenticate and gain access"""
    username = entry1.get().lower()
    password = entry2.get()

    if not len(username or password) < 1:
        try:
            # Opens the logininfo.txt file for reading
            db = open("DB\\logininfo.txt", "r")
            for i in db:
                user_id, stored_username, stored_password = i.strip().split(", ")
                if stored_username.lower() == username:
                    stored_password = stored_password[2:-1]
                    stored_password = stored_password.encode('utf-8')
                    if bcrypt.checkpw(password.encode('utf-8'),
                    stored_password):
                        with open("DB\\current_user.txt", "w") as user_file:
                            user_file.write(f"{user_id}, {stored_username}")
                        tkinter.messagebox.showinfo("Success", 
                        f"Successfully Logged In!\nHi, {stored_username}")
                        open_home()
                        return

            tkinter.messagebox.showerror("Error",
            "Incorrect Username Or Password")
        except:
            tkinter.messagebox.showerror("Error", "Incorrect Password")
    else:
        tkinter.messagebox.showerror("Error", "Please Try Again")


def login():
    gainAccess()


def open_signup():
    """Function to open the signup.py file"""
    root.destroy()
    subprocess.run(["python", "signup.py"])


def open_home():
    """Function to open the home2.py file"""
    root.destroy()
    subprocess.run(["python", "home2.py"])

# GUI
frame = customtkinter.CTkFrame(master = root)
frame.pack(pady = 20, padx = 60, fill = "both", expand = True)

label = customtkinter.CTkLabel(master = frame,
text = "Welcome!", font = ("Blinker", 25))
label.pack(pady = 12, padx = 10)

entry1 = customtkinter.CTkEntry(master = frame, placeholder_text = "Username")
entry1.pack(padx = 10, pady = 12)

entry2 = customtkinter.CTkEntry(master = frame,
placeholder_text = "Password", show = "*")
entry2.pack(padx = 10, pady = 12)

login_button = customtkinter.CTkButton(master = frame,
text = "Login", command = login)
login_button.pack(pady = 12, padx = 10)

# Button allows users to easily navigate to the signup page
signup_label = customtkinter.CTkLabel(master = frame,
text = "Don't have an account? Click Here!",
font = ("Blinker", 10), cursor = "hand2", fg_color = "#E5E5E5")
signup_label.pack(pady = 5)
signup_label.bind("<Button-1>", lambda event: open_signup())

root.mainloop()
