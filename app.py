import streamlit as st
import json
from utils import *
from ai import enhance_text_with_ai
from db import *
import folium
from streamlit_tags import st_tags
from folium.plugins import HeatMap
from streamlit_folium import st_folium

# Inizializza lo stato della sessione
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}

# Sidebar navigation
st.sidebar.title("Navigazione")
page = st.sidebar.radio(
    "Seleziona una pagina",
    ["Informazioni", "Segnalazione", "Gestione Segnalazioni"])

if page == "Informazioni":
    st.title("📄 Informazioni su UrbanAIdea")
    st.write("""
    UrbanAIdea è un'iniziativa innovativa che utilizza l'intelligenza artificiale 
    per migliorare la gestione delle segnalazioni urbane.
    """)
    st.image("https://via.placeholder.com/800x400",
             caption="Smart City powered by AI")
    st.write("Per tornare all'applicazione principale, usa la barra laterale.")
elif page == "Segnalazione":
    st.title("⚠️ Segnalazione")
    steps = ["Dati Utente", "Segnalazione Problema", "Riepilogo"]
    st.progress((st.session_state.step - 1) / (len(steps) - 1))
    st.subheader(
        f"Passo {st.session_state.step}: {steps[st.session_state.step - 1]}")

    # Existing steps for user data, issue reporting, and summary
    # Step 1: Dati utente
    if st.session_state.step == 1:
        nome = st.text_input("Nome",
                             st.session_state.user_data.get('nome', ''))
        cognome = st.text_input("Cognome",
                                st.session_state.user_data.get('cognome', ''))
        email = st.text_input("Email",
                              st.session_state.user_data.get('email', ''))
        cellulare = st.text_input(
            "Cellulare", st.session_state.user_data.get('cellulare', ''))

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

    # Step 2: Segnalazione problema
    elif st.session_state.step == 2:
        posizione = st.text_input(
            "Posizione/Via del problema",
            st.session_state.user_data.get('posizione', ''))

        # Gestisci il testo della descrizione direttamente tramite session state
        if 'descrizione' not in st.session_state.user_data:
            st.session_state.user_data['descrizione'] = ""
        descrizione = st.text_area("Descrizione del problema",
                                   st.session_state.user_data['descrizione'])

        # Bottone per migliorare con l'AI
        if st.button("✨ Migliora con l'AI"):
            response_text, generated_tags = enhance_text_with_ai(descrizione)
            st.session_state.user_data['descrizione'] = response_text
            st.session_state.user_data['labels'] = generated_tags
            st.rerun()  # Aggiorna l'interfaccia immediatamente

        # Mostra i tags generati, se presenti
        if 'labels' in st.session_state.user_data:
            tags = st.session_state.user_data['labels'].strip("[]")
            keywords = st_tags(label='Tags generati:',
                            text='Press enter to add more',
                            value=tags.split(","),
                            maxtags=4,
                            key='1')

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Indietro"):
                prev_step()
        with col2:
            if st.button("Avanti"):
                if not posizione:
                    st.error("La posizione del problema è obbligatoria.")
                elif len(descrizione) < 10:
                    st.error(
                        "La descrizione deve contenere almeno 10 caratteri.")
                else:
                    st.session_state.user_data.update({
                        "posizione":
                        posizione,
                        "descrizione":
                        st.session_state.user_data[
                            'descrizione']  # Usa il valore aggiornato
                    })
                    next_step()

    # Step 3: Riepilogo
    elif st.session_state.step == 3:
        labels = st.session_state.user_data['labels']

        st.write("### Dati Utente")
        st.write(st.session_state.user_data)

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Indietro"):
                prev_step()
        with col2:
            if st.button("Modifica"):
                st.session_state.step = 1
                st.rerun()
        with col3:
            if st.button("Conferma"):
                json_data = json.dumps(st.session_state.user_data, indent=2)
                st.download_button(
                    label="Scarica JSON",
                    data=json_data,
                    file_name="segnalazione.json",
                    mime="application/json",
                )
                st.success("Segnalazione inviata con successo!")
                if st.button("Nuova Segnalazione"):
                    st.session_state.step = 1
                    st.session_state.user_data = {}
                    st.rerun()

elif page == "Gestione Segnalazioni":
    st.title("🗺️ Mappa segnalazioni su UrbanAIdea")

    # Estrai i dati dal database
    df = get_all_reports()

    # Get the first report's coordinates (or choose any other logic you prefer)
    first_report_coords = df.iloc[0]['coordinates'].split(',')
    lat, lon = float(first_report_coords[0].strip()), float(
        first_report_coords[1].strip())

    # Crea una mappa Folium con il centro sulle coordinate del primo report
    m = folium.Map(location=[lat, lon], zoom_start=12)

    # Prepara i dati per la HeatMap (le coordinate di tutti i report)
    heat_data = []
    for index, row in df.iterrows():
        coordinates = row['coordinates'].split(',')
        lat, lon = float(coordinates[0].strip()), float(
            coordinates[1].strip())  # Converti in float per lat e lon
        heat_data.append(
            [lat, lon])  # Aggiungi le coordinate alla lista per la HeatMap

    # Sidebar per selezionare il tipo di visualizzazione della mappa
    map_view = st.sidebar.radio(
        "Seleziona il tipo di visualizzazione della mappa",
        ["Heatmap", "Marker"])

    # Setup del database (opzionale)
    if st.sidebar.button("Setup DB"):
        setup_db()

    if map_view == "Heatmap":
        # Aggiungi la HeatMap sulla mappa
        HeatMap(heat_data).add_to(m)
    elif map_view == "Marker":
        # Aggiungi i marker per ogni segnalazione nel database
        for index, row in df.iterrows():
            coordinates = row['coordinates'].split(',')
            lat, lon = float(coordinates[0].strip()), float(
                coordinates[1].strip())  # Converti in float per lat e lon

            # Aggiungi un marker sulla mappa
            folium.Marker(
                location=[lat, lon],
                popup=f"Segnalazione: {row['name']}\n{row['description']}",
                tooltip=row['name']).add_to(m)

    # Rendi visibile la mappa in Streamlit
    st_folium(m, width=800, height=500)

    # Mostra la tabella con le segnalazioni
    display_table(df)
