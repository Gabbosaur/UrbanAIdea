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


# def generate_labels(description):
#     # Dizionario di parole chiave e relative etichette
#     keywords = {
#         'strada': 'Problema stradale',
#         'illuminazione': 'Problema di illuminazione',
#         'rifiuti': 'Problema di rifiuti',
#         'parco': 'Problema in area verde',
#         'edificio': 'Problema strutturale',
#         'rumore': 'Inquinamento acustico',
#         'acqua': 'Problema idrico'
#     }
#     description_lower = description.lower()
#     labels = [
#         label for keyword, label in keywords.items()
#         if keyword in description_lower
#     ]
#     return labels if labels else ["indefinito"]


def split_message_and_tags(text):
    """
    Divide il testo in due parti: messaggio e tags.
    I tags devono essere preceduti da 'tags:' (case-insensitive).

    Args:
        text (str): Il testo da analizzare.

    Returns:
        tuple: Una tupla contenente (messaggio, tags).
    """
    # Cerca il punto di inizio dei tags
    split_marker = "tags:"
    parts = text.lower().split(split_marker)

    if len(parts) > 1:
        message = parts[0].strip()  # Parte prima di "tags:"
        tags = parts[1].strip()  # Parte dopo "tags:"
    else:
        message = text.strip()  # Testo completo senza "tags:"
        tags = ""  # Nessun tag trovato

    return message, tags




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
    

def extract_filters(df):
    # Drop the 'id' and 'coordinates' columns (they are retained in df, but not displayed)
    df_display = df.drop(columns=["id", "coordinates", "name"])

    # Gestione speciale per il campo 'tag'
    if "tag" in df_display.columns:
        # Crea un set di tag unici separati da virgola
        unique_tags = set(
            tag.strip()
            for tags in df_display["tag"].dropna()
            for tag in tags.split(",")
        )
        selected_tag = st.sidebar.selectbox("Filter by Tag", ["All"] + list(unique_tags))
    else:
        selected_tag = "All"

    # Display filters for each column dynamically (excluding 'id', 'coordinates', and 'tag')
    filters = {}
    for column in df_display.columns:
        if column != "tag":  # Gestione separata per 'tag'
            unique_values = df_display[column].dropna().unique()
            filter_widget = st.sidebar.selectbox(f"Filter by {column}",
                                                 ["All"] + list(unique_values))
            filters[column] = filter_widget

    # Apply the filters to the DataFrame
    for column, filter_value in filters.items():
        if filter_value != "All":
            df_display = df_display[df_display[column] == filter_value]

    # Filtro personalizzato per il campo 'tag'
    if selected_tag != "All":
        df_display = df_display[df_display["tag"].str.contains(
            rf'\b{selected_tag}\b', na=False)]  # Filtra le righe che contengono il tag selezionato

    # Ritorna il DataFrame filtrato
    return df[df.index.isin(df_display.index)]

