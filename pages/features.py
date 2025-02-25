import requests
import folium
import streamlit as st
from streamlit_folium import folium_static
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut


def get_location(city):
    geolocator = Nominatim(user_agent="med-bot-app", timeout=5)  # Increased timeout
    try:
        location = geolocator.geocode(city)
        if location:
            return location.latitude, location.longitude
        else:
            st.error("❌ Could not find location. Please enter a valid city.")
            return None, None
    except GeocoderTimedOut:
        st.error("⏳ Location lookup timed out. Please try again.")
        return None, None
    except Exception as e:
        st.error(f"⚠ Location lookup failed: {e}")
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
        response = requests.get(overpass_url, params={'data': query}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("elements", [])
        else:
            st.error("❌ Failed to fetch clinic data. Please try again later.")
            return []
    except requests.exceptions.Timeout:
        st.error("⏳ Request to fetch clinics timed out. Try again.")
        return []
    except Exception as e:
        st.error(f"⚠ Error fetching clinics: {e}")
        return []


st.title("🏥 Nearby Medical Clinics")

city = st.text_input("📍 Enter Your City:", "Delhi")

latitude, longitude = get_location(city)

if latitude and longitude:
    st.write(f"**📍 Detected Location:** {latitude}, {longitude}")

    clinics = fetch_nearby_clinics(latitude, longitude)

    # Initialize map centered on detected location
    m = folium.Map(location=[latitude, longitude], zoom_start=13)

    if clinics:
        st.success(f"✅ Found {len(clinics)} clinics near {city}")

        # Add clinic markers
        for clinic in clinics:
            lat = clinic["lat"]
            lon = clinic["lon"]
            folium.Marker(
                [lat, lon], 
                popup="Clinic", 
                icon=folium.Icon(color="red")
            ).add_to(m)
    else:
        st.warning("⚠ No clinics found in your area. Try another city.")

    # Display map
    folium_static(m)
else:
    st.error("🚨 Please enter a valid city name.")
