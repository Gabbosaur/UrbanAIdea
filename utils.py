import streamlit as st
import googlemaps
import re
import os

def next_step():
    st.session_state.step += 1
    st.rerun()

def prev_step():
    st.session_state.step -= 1
    st.rerun()

def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    pattern = r'^\+?1?\d{9,15}$'
    return re.match(pattern, phone) is not None

def generate_labels(description):
    # Dizionario di parole chiave e relative etichette
    keywords = {
        'strada': 'Problema stradale',
        'illuminazione': 'Problema di illuminazione',
        'rifiuti': 'Problema di rifiuti',
        'parco': 'Problema in area verde',
        'edificio': 'Problema strutturale',
        'rumore': 'Inquinamento acustico',
        'acqua': 'Problema idrico'
    }
    description_lower = description.lower()
    labels = [label for keyword, label in keywords.items() if keyword in description_lower]
    return labels if labels else ["Indefinito"]



# Function to convert address to coordinates using Google Maps API
def get_coordinates_google(address):
    gmaps = googlemaps.Client(key=os.environ.get("GOOGLE_MAPS_API_KEY"))
    geocode_result = gmaps.geocode(address)
    if geocode_result:
        lat = geocode_result[0]["geometry"]["location"]["lat"]
        lon = geocode_result[0]["geometry"]["location"]["lng"]
        return lat, lon
    else:
        st.error(f"Unable to find coordinates for address: {address}")
        return None, None
    

def display_table(df):
    # Drop the 'id' and 'coordinates' columns (they are retained in df, but not displayed)
    df_display = df.drop(columns=["id", "coordinates", "name"])

    # Display filters for each column dynamically (excluding 'id' and 'coordinates')
    filters = {}
    for column in df_display.columns:
        unique_values = df_display[column].dropna().unique()
        filter_widget = st.sidebar.selectbox(f"Filter by {column}",
                                             ["All"] + list(unique_values))
        filters[column] = filter_widget

    # Apply the filters to the DataFrame
    for column, filter_value in filters.items():
        if filter_value != "All":
            df_display = df_display[df_display[column] == filter_value]

    # Return the filtered DataFrame for further use
    return df[df.index.isin(df_display.index)]
