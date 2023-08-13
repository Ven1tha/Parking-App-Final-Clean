"""Allows users to list and book parking spaces"""
import tkinter as tk
from tkinter import messagebox, simpledialog
import re
import requests
from cryptography.fernet import Fernet

# Defining the Nominatim API endpoint
NOMINATIM_ENDPOINT = "https://nominatim.openstreetmap.org/search"

# Defining the file for encryption key storage
ENCRYPTION_KEY_FILE = "encryption_key.key"


def load_encryption_key():
    """Functions for encryption key management"""
    try:
        with open(ENCRYPTION_KEY_FILE, "rb") as key_file:
            return key_file.read()
    except FileNotFoundError:
        return None


def save_encryption_key(key):
    """"Saves the encryption key file"""
    with open(ENCRYPTION_KEY_FILE, "wb") as key_file:
        key_file.write(key)


def generate_or_load_encryption_key():
    """Loads or genertes an encryption key when needed"""
    loaded_key = load_encryption_key()
    if loaded_key:
        return loaded_key
    else:
        new_key = Fernet.generate_key()
        save_encryption_key(new_key)
        return new_key

# Initialises encryption key and cipher suite
encryption_key = generate_or_load_encryption_key()
cipher_suite = Fernet(encryption_key)


def encrypt(text):
    """Encryption function"""
    return cipher_suite.encrypt(text.encode()).decode()


def decrypt(encrypted_text):
    """Decypt function"""
    return cipher_suite.decrypt(encrypted_text.encode()).decode()


def read_listings():
    """Function to read and decrypt listings from the file"""
    listings = []
    with open("DB/listings.txt", "r") as file:
        for line in file:
            try:
                key, encrypted_listing, hourly_price = line.strip().split(",", 2)
                if key == encryption_key.decode():
                    decrypted_listing = decrypt(encrypted_listing)
                    listings.append((decrypted_listing, hourly_price))
            except Exception as e:
                print(f"Error decrypting listing: {e}")
                # Handles decryption errors
    return listings


def autocomplete_address(input_text):
    """Function to autocomplete address using Nominatim API"""
    params = {
        "format": "json",
        "q": input_text
    }
    response = requests.get(NOMINATIM_ENDPOINT, params=params)
    data = response.json()
    suggestions = [result["display_name"] for result in data]
    return suggestions


def validate_address(address):
    """Function to validate address using Nominatim API"""
    params = {
        "format": "json",
        "q": address
    }
    response = requests.get(NOMINATIM_ENDPOINT, params=params)
    data = response.json()
    return len(data) > 0


def list_parking_space():
    """Function to list a parking space"""
    global entry_house_number, entry_street_name, entry_city, listbox_available_spaces

    house_number = entry_house_number.get()
    street_name = entry_street_name.get()
    city = entry_city.get()

    # Ensure the inputs are English
    if not re.match(r'^[a-zA-Z\s]+$', street_name) or not re.match(r'^[a-zA-Z\s]+$', city):
        messagebox.showwarning("Warning", 
        "All input boxes should be filled and" 
        " contain only English alphabetic characters and numbers for the House Number.")
        return

    if house_number and street_name and city:
        full_address = f"{house_number}, {street_name}, {city}"

        # Check if the address is already listed in the listbox
        if full_address in listbox_available_spaces.get(0, tk.END):
            messagebox.showwarning("Warning", "This address is already listed.")
            return

        # Check if the address is already listed in the listings.txt file
        with open("DB/listings.txt", "r") as listings_file:
            for line in listings_file:
                key, encrypted_listing = line.strip().split(",", 1)
                decrypted_listing = decrypt(encrypted_listing)
                if decrypted_listing == full_address:
                    messagebox.showwarning("Warning", "This address is already listed.")
                    return

        # Check if all three input fields have the same value
        if (
            street_name == city
        ):
            messagebox.showerror("Error", "Please enter different values for each field.")
            return

        # Validates the address
        if not validate_address(full_address):
            messagebox.showwarning("Warning", "Invalid address. Please enter a valid address.")
            return

        # Prompts the user for hourly price
        hourly_price = simpledialog.askfloat("Hourly Price", 
        "Enter hourly price for the parking space:")
        if hourly_price is None:
            return  # If the User canceled then return

        encrypted_address = encrypt(full_address)

        with open("DB/listings.txt", "a") as file:
            file.write(f"{encryption_key.decode()},{encrypted_address},{hourly_price}\n")

        display_text = f"{full_address} - Hourly Price: {hourly_price}"
        listbox_available_spaces.insert(tk.END, display_text)
        entry_house_number.delete(0, tk.END)
        entry_street_name.delete(0, tk.END)
        entry_city.delete(0, tk.END)

        messagebox.showinfo("Success", "Parking space listed successfully!")
    else:
        messagebox.showwarning("Warning", "Please fill in all the fields!")


def book_parking_space():
    """Function to book a parking space"""
    global listbox_available_spaces

    selected_space = listbox_available_spaces.curselection()

    if not selected_space:
        messagebox.showwarning("Warning", "Please select a parking space!")
        return

    selected_space = selected_space[0]

    with open("DB/listings.txt", "r") as file:
        listings = file.readlines()

    selected_listing_parts = listings[selected_space].strip().split(",", 2)

    if len(selected_listing_parts) != 3:  # Verify if the split produces three parts
        messagebox.showerror("Error", "Invalid listing format in listings.txt")
        return

    selected_listing, hourly_price = selected_listing_parts[1], selected_listing_parts[2]  # Skips the encryption key

    address = decrypt(selected_listing)

    try:
        with open("DB/current_user.txt", "r") as current_user_file:
            user_id, username = current_user_file.read().strip().split(", ")
    except FileNotFoundError:
        messagebox.showerror("Error", "current_user.txt not found!")
        return
    except ValueError:
        messagebox.showerror("Error", "Invalid format in current_user.txt")
        return

    duration = simpledialog.askinteger("Booking Duration", "Enter booking duration in hours:")
    if duration is None:
        return  # If the User canceled then return

    total_cost = float(hourly_price) * duration

    encrypted_selected_listing = encrypt(selected_listing)

    with open("DB/bookings.txt", "a") as bookings_file:
        bookings_file.write(f"{user_id}, {username}, {encrypted_selected_listing}, {duration}, {total_cost:.2f}\n")

    with open("DB/listings.txt", "w") as listings_file:
        for i, listing in enumerate(listings):
            if i != selected_space:
                listings_file.write(listing)

    listbox_available_spaces.delete(selected_space)

    # Imports and calls the show_summary_page function
    from summary import show_summary_page
    booking_info = (username, float(hourly_price), duration, total_cost)
    show_summary_page(booking_info, address)


def create_home_page():
    """Function to create the home page GUI"""
    global entry_house_number, entry_street_name, entry_city, listbox_available_spaces

    home_page = tk.Tk()
    home_page.title("Home Page")

    label_heading = tk.Label(home_page, text="Home Page", font=("Helvetica", 20))
    label_heading.pack(pady=10)

    frame_list_parking = tk.Frame(home_page)
    frame_list_parking.pack(pady=10)

    label_house_number = tk.Label(frame_list_parking, text="House Number:")
    label_house_number.grid(row=0, column=0)
    entry_house_number = tk.Entry(frame_list_parking)
    entry_house_number.grid(row=0, column=1)

    label_street_name = tk.Label(frame_list_parking, text="Street Name:")
    label_street_name.grid(row=1, column=0)
    entry_street_name = tk.Entry(frame_list_parking)
    entry_street_name.grid(row=1, column=1)

    label_city = tk.Label(frame_list_parking, text="City:")
    label_city.grid(row=2, column=0)
    entry_city = tk.Entry(frame_list_parking)
    entry_city.grid(row=2, column=1)

    button_list_parking = tk.Button(frame_list_parking, text="List Parking Space",
    command=list_parking_space)
    button_list_parking.grid(row=3, column=0, columnspan=2, pady=10)

    frame_book_parking = tk.Frame(home_page)
    frame_book_parking.pack(pady=10)

    label_available_spaces = tk.Label(frame_book_parking, text="Available Parking Spaces:")
    label_available_spaces.pack()

    scrollbar_available_spaces = tk.Scrollbar(frame_book_parking)
    scrollbar_available_spaces.pack(side=tk.RIGHT, fill=tk.Y)

    listbox_available_spaces = tk.Listbox(frame_book_parking,
    yscrollcommand=scrollbar_available_spaces.set)
    listbox_available_spaces.pack(fill=tk.BOTH, expand=True)

    listings = read_listings()
    for listing, hourly_price in listings:
        display_text = f"{listing} - Hourly Price: {hourly_price}"
        listbox_available_spaces.insert(tk.END, display_text)

    scrollbar_available_spaces.config(command=listbox_available_spaces.yview)

    button_book_parking = tk.Button(frame_book_parking, text="Book Parking Space",
    command=book_parking_space)
    button_book_parking.pack(pady=10)

    # Starts the main GUI loop
    home_page.mainloop()


def main():
    """Main function to start the application"""
    root = tk.Tk()
    root.withdraw()  # Hides the main root window

    # Explicitly creates and opens the home page as the main application window
    create_home_page()

    root.mainloop()

if __name__ == "__main__":
    main()