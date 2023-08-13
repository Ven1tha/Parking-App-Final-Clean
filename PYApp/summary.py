"""Displays the map and summary data after booking"""
import tkinter as tk
import requests
import webview
import folium
from folium import IFrame

#Defines the Mapbox API access token
MAPBOX_ACCESS_TOKEN = "pk.eyJ1IjoibmlnZXJpYW5wcmluY2UiLCJhIjoiY2xrZzBqeXR4MTZscjNlczRzNGJzZTQ2dyJ9.HXMHqRz1_umaam16lvKQFw"


def get_coordinates_from_address(address):
    """Function to retrieve coordinates from an address using Mapbox API"""
    geocoding_endpoint = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{address}.json"

    params = {
        "access_token": MAPBOX_ACCESS_TOKEN
    }

    response = requests.get(geocoding_endpoint, params = params)
    data = response.json()

    if data.get("features"):
        coordinates = data["features"][0]["geometry"]["coordinates"]
        return coordinates[0], coordinates[1]
    else:
        print("Error retrieving coordinates.")
        return None


def show_summary_page(booking_info, address):
    """Function to display the booking summary page with map"""
    summary_page = tk.Tk()
    summary_page.title("Booking Summary")

    username, hourly_price, duration, total_cost = booking_info

    # Labels to display booking details
    summary_label = tk.Label(summary_page, 
    text = "Booking Summary", font = ("Helvetica", 20))
    summary_label.pack(pady=10)

    username_label = tk.Label(summary_page, text = f"Username: {username}")
    username_label.pack()

    address_label = tk.Label(summary_page, text = f"Address: {address}")
    address_label.pack()

    hourly_price_label = tk.Label(summary_page,
    text = f"Hourly Price: ${hourly_price:.2f}")
    hourly_price_label.pack()

    duration_label = tk.Label(summary_page,
    text = f"Duration: {duration} hours")
    duration_label.pack()

    total_cost_label = tk.Label(summary_page,
    text = f"Total Cost: ${total_cost:.2f}")
    total_cost_label.pack()

    # Gets coordinates from the address
    lng, lat = get_coordinates_from_address(address)

    if lng is not None and lat is not None:
        # Creates a folium map with a marker for the address
        m = folium.Map(location = [lat, lng], zoom_start = 15)
        folium.Marker([lat, lng], popup = IFrame(html = f"Address: {address}",
        width = 300, height = 100)).add_to(m)

        map_html = "map.html"
        m.save(map_html)

        # Uses webview to display the map
        webview.create_window("Booking Map",
        map_html, width = 800, height = 600)
        webview.start()
    else:
        print("Coordinates not available for the address.")

    summary_page.mainloop() # Starts the summary page GUI loop
