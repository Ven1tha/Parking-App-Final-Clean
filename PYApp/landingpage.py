"""This is my landing page. 
The first thing that'll open when the program is run."""
import tkinter as tk
from tkinter import ttk
import subprocess
from PIL import ImageTk, Image


def open_next_page():
    """Closes the old window before opening a new one"""
    window.destroy()

    # Function to handle button click and navigate to the next page
    subprocess.run(['python', 'login.py'])
    pass

# Creates the main window
window = tk.Tk()

# Sets window properties
window.title("Parking Solutions")
window.geometry("800x600")  # Sets the desired window size

# Loads the background image
image = Image.open("Assets/landingimage.jpg")
# Resizes the image to fit the window
image = image.resize((800, 600), Image.LANCZOS)
background_image = ImageTk.PhotoImage(image)

# Creates a canvas to place the image and overlay
canvas = tk.Canvas(window, width = 800, height = 600)
canvas.pack(fill = "both", expand = True)

# Displays the background image
canvas.create_image(0, 0, image = background_image, anchor = "nw")

# Adds text overlay
text = canvas.create_text(400, 200, text = "Parking Solutions",
font = ("Arial", 30, 'bold'), fill = "white", justify = "center")

# Creates a style for the button
style = ttk.Style()
style.configure("TButton", foreground = "black",
background = "#0390fc", font = ("Heebo", 14), width = 20)

# Creates the Login button
button = ttk.Button(window, text = "Login",
command = open_next_page, style = "TButton")
button_window = canvas.create_window(400, 400,
anchor = "center", window = button)

window.mainloop()
