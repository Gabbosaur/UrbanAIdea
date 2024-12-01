import sqlite3
import streamlit as st
import json
from utils import *
from ai import enhance_text_with_ai
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import pandas as pd


# Function to initialize the SQLite database
def setup_db():
    create_table()
    populate_db_from_excel("dataset.xlsx")
    st.success("Database setup completed successfully!")



def create_table():
    conn = sqlite3.connect("reports.db")
    cursor = conn.cursor()
    
    # Drop the old table if it exists
    cursor.execute("DROP TABLE IF EXISTS report")
    
    # Create the new 'report' table with the provided schema
    cursor.execute("""
        CREATE TABLE report (
            id INTEGER,
            coordinates TEXT,
            name TEXT,
            address TEXT,
            district TEXT,
            zone TEXT,
            tag TEXT,
            description TEXT,
            reporter_name TEXT,
            reporter_surname TEXT,
            reporter_email TEXT,
            reporter_phone NUMERIC,
            PRIMARY KEY(id AUTOINCREMENT)
        )
    """)
    conn.commit()
    conn.close()
    st.success("Database table created successfully!")


def populate_db_from_excel(excel_file):
    # Read the Excel file
    df = pd.read_excel(excel_file)

    # Check if the required columns are in the Excel file
    required_columns = ['Geo Point', 'Nome', 'Quartiere', 'Zona di prossimità', 'Tag', 'Descrizione']
    if not all(col in df.columns for col in required_columns):
        st.error("Excel file missing required columns.")
        return
    
    # Connect to the SQLite database
    conn = sqlite3.connect("reports.db")
    cursor = conn.cursor()

    # Prepare the SQL query to insert data
    insert_query = """
        INSERT INTO report (coordinates, name, district, zone, tag, description)
        VALUES (?, ?, ?, ?, ?, ?)
    """

    # Loop through each row in the DataFrame and insert into the database
    for index, row in df.iterrows():
        coordinates = row['Geo Point']
        name = row['Nome']
        district = row['Quartiere']
        zone = row['Zona di prossimità']
        tag = row['Tag']
        description = row['Descrizione']

        # Insert the row into the database
        cursor.execute(insert_query, (coordinates, name, district, zone, tag, description))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    st.success("Database populated successfully from Excel!")


def get_all_reports():
    # Connect to the SQLite database
    conn = sqlite3.connect("reports.db")
    
    # Query to select all data from the 'report' table
    query = "SELECT * FROM report"
    
    # Read the data into a pandas DataFrame
    df = pd.read_sql(query, conn)
    
    # Close the database connection
    conn.close()
    return df

def display_table(df):
        # Drop the 'id' and 'coordinates' columns (they are retained in df, but not displayed)
    df_display = df.drop(columns=["id", "coordinates"])

    # Display filters for each column dynamically (excluding 'id' and 'coordinates')
    filters = {}
    for column in df_display.columns:
        unique_values = df_display[column].dropna().unique()  # Get unique values for each column
        filter_widget = st.sidebar.selectbox(f"Filter by {column}", ["All"] + list(unique_values))
        filters[column] = filter_widget

    # Apply the filters to the DataFrame
    for column, filter_value in filters.items():
        if filter_value != "All":
            df_display = df_display[df_display[column] == filter_value]

    # Display the filtered DataFrame in Streamlit
    st.dataframe(df_display)



# Inizializza lo stato della sessione
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}


# Sidebar navigation
st.sidebar.title("Navigazione")
page = st.sidebar.radio("Seleziona una pagina", ["Informazioni", "Segnalazione", "Gestione Segnalazioni"])

if page == "Informazioni":
    st.title("📄 Informazioni su UrbanAIdea")
    st.write("""
    UrbanAIdea è un'iniziativa innovativa che utilizza l'intelligenza artificiale 
    per migliorare la gestione delle segnalazioni urbane.
    """)
    st.image("https://via.placeholder.com/800x400", caption="Smart City powered by AI")
    st.write("Per tornare all'applicazione principale, usa la barra laterale.")
elif page == "Segnalazione":
    st.title("📄 Segnalazione")
    steps = ["Dati Utente", "Segnalazione Problema", "Riepilogo"]
    st.progress((st.session_state.step - 1) / (len(steps) - 1))
    st.subheader(f"Passo {st.session_state.step}: {steps[st.session_state.step - 1]}")

    # Existing steps for user data, issue reporting, and summary
    # Step 1: Dati utente
    if st.session_state.step == 1:
        nome = st.text_input("Nome", st.session_state.user_data.get('nome', ''))
        cognome = st.text_input("Cognome", st.session_state.user_data.get('cognome', ''))
        email = st.text_input("Email", st.session_state.user_data.get('email', ''))
        cellulare = st.text_input("Cellulare", st.session_state.user_data.get('cellulare', ''))
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Avanti"):
                if not nome or not cognome:
                    st.error("Nome e Cognome sono campi obbligatori.")
                elif not validate_email(email):
                    st.error("Inserisci un indirizzo email valido.")
                elif not validate_phone(cellulare):
                    st.error("Inserisci un numero di cellulare valido.")
                else:
                    st.session_state.user_data.update({
                        "nome": nome,
                        "cognome": cognome,
                        "email": email,
                        "cellulare": cellulare
                    })
                    next_step()
    # More steps...
elif page == "Gestione Segnalazioni":
    st.title("📄 Gestione segnalazioni su UrbanAIdea")

    # Estrai i dati dal database
    df = get_all_reports()

    # Get the first report's coordinates (or choose any other logic you prefer)
    first_report_coords = df.iloc[0]['coordinates'].split(',')
    lat, lon = float(first_report_coords[0].strip()), float(first_report_coords[1].strip())

    # Crea una mappa Folium con il centro sulle coordinate del primo report
    m = folium.Map(location=[lat, lon], zoom_start=12)

    # Prepara i dati per la HeatMap (le coordinate di tutti i report)
    heat_data = []
    for index, row in df.iterrows():
        coordinates = row['coordinates'].split(',')
        lat, lon = float(coordinates[0].strip()), float(coordinates[1].strip())  # Converti in float per lat e lon
        heat_data.append([lat, lon])  # Aggiungi le coordinate alla lista per la HeatMap

    # Sidebar per selezionare il tipo di visualizzazione della mappa
    map_view = st.sidebar.radio("Seleziona il tipo di visualizzazione della mappa", ["Heatmap", "Marker"])

    if map_view == "Heatmap":
        # Aggiungi la HeatMap sulla mappa
        HeatMap(heat_data).add_to(m)
    elif map_view == "Marker":
        # Aggiungi i marker per ogni segnalazione nel database
        for index, row in df.iterrows():
            coordinates = row['coordinates'].split(',')
            lat, lon = float(coordinates[0].strip()), float(coordinates[1].strip())  # Converti in float per lat e lon

            # Aggiungi un marker sulla mappa
            folium.Marker(
                location=[lat, lon],
                popup=f"Segnalazione: {row['name']}\n{row['description']}",
                tooltip=row['name']
            ).add_to(m)

    # Rendi visibile la mappa in Streamlit
    st_folium(m, width=800, height=500)

    # Setup del database (opzionale)
    if st.button("Setup DB"):
        setup_db()

    # Mostra la tabella con le segnalazioni
    display_table(df)
    

