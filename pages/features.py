import requests
import folium
import streamlit as st
from streamlit_folium import folium_static
from geopy.geocoders import Nominatim


def get_location(city):
    geolocator = Nominatim(user_agent="med-bot-app")
    try:
        location = geolocator.geocode(city)
        if location:
            return location.latitude, location.longitude
        else:
            st.error("Could not find location. Please enter a valid city.")
            return None, None
    except Exception as e:
        st.error(f"Location lookup failed: {e}")
        return None, None

def fetch_nearby_clinics(lat, lon):
    overpass_url = "http://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    node
      [amenity=clinic]
      (around:5000, {lat}, {lon});
    out;
    """
    try:
        response = requests.get(overpass_url, params={'data': query})
        if response.status_code == 200:
            data = response.json()
            return data.get("elements", [])
        else:
            st.error("Failed to fetch clinic data. Try again later.")
            return []
    except Exception as e:
        st.error(f"Error fetching clinics: {e}")
        return []

st.title("Nearby Medical Clinics")

city = st.text_input("Enter Your City:", "Delhi")

latitude, longitude = get_location(city)

if latitude and longitude:
    st.write(f"**Detected Location:** {latitude}, {longitude}")

    clinics = fetch_nearby_clinics(latitude, longitude)

    if clinics:
        st.success(f"✅ Found {len(clinics)} clinics near {city}")

        
        m = folium.Map(location=[latitude, longitude], zoom_start=13)

        for clinic in clinics:
            lat = clinic["lat"]
            lon = clinic["lon"]
            folium.Marker([lat, lon], popup="Clinic", icon=folium.Icon(color="red")).add_to(m)

        folium_static(m) 
    else:
        st.warning("⚠ No clinics found in your area. Try another city.")
else:
    st.error("Please enter a valid city name.")

