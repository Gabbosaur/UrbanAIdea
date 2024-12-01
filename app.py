import streamlit as st
import json
from utils import *
from ai import enhance_text_with_ai
from db import *
import folium
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
    st.title("📄 Segnalazione")
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

        # Bottone per convertire in maiuscolo
        if st.button("✨ Migliora con l'AI"):
            st.session_state.user_data['descrizione'] = enhance_text_with_ai(
                descrizione)
            st.rerun()  # Aggiorna l'interfaccia immediatamente

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
        labels = generate_labels(st.session_state.user_data['descrizione'])
        st.session_state.user_data['labels'] = labels

        st.write("### Dati Utente")
        st.write(st.session_state.user_data)
        st.write("### Segnalazione")
        st.write(f"Etichette: {', '.join(labels)}")

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
                lat, lon = get_coordinates_google(st.session_state.user_data['posizione'])
                st.session_state.user_data.update({
                    "coordinate": f"{lat}, {lon}"
                })
                insert_data(st.session_state.user_data)
                st.success("Segnalazione inviata con successo!")
                if st.button("Nuova Segnalazione"):
                    st.session_state.step = 1
                    st.session_state.user_data = {}
                    st.rerun()

# Pagina "Gestione Segnalazioni"
elif page == "Gestione Segnalazioni":
    st.title("📄 Gestione segnalazioni su UrbanAIdea")

    # Estrai i dati dal database
    df = get_all_reports()

    # Filtra i dati usando la funzione display_table
    filtered_df = display_table(df)

    # Controlla se ci sono coordinate nei dati filtrati
    if not filtered_df.empty and "coordinates" in filtered_df.columns:
        # Prepara i dati per la mappa (heatmap e marker)
        heat_data = []
        for _, row in filtered_df.iterrows():
            if row['coordinates']:
                coordinates = row['coordinates'].split(',')
                lat, lon = float(coordinates[0].strip()), float(coordinates[1].strip())
                heat_data.append([lat, lon])

        # Sidebar per selezionare il tipo di visualizzazione della mappa
        map_view = st.sidebar.radio(
            "Seleziona il tipo di visualizzazione della mappa",
            ["Heatmap", "Marker"])

        # Crea la mappa con il centro sulla prima coordinata filtrata
        if heat_data:
            lat, lon = heat_data[0]
            m = folium.Map(location=[lat, lon], zoom_start=12)

            if map_view == "Heatmap":
                HeatMap(heat_data).add_to(m)
            elif map_view == "Marker":
                for _, row in filtered_df.iterrows():
                    if row['coordinates']:
                        coordinates = row['coordinates'].split(',')
                        lat, lon = float(coordinates[0].strip()), float(coordinates[1].strip())
                        folium.Marker(
                            location=[lat, lon],
                            popup=f"Segnalazione: {row['name']}\n{row['description']}",
                            tooltip=row['name']).add_to(m)

            # Rendi visibile la mappa in Streamlit sopra la tabella
            st_folium(m, width=800, height=500)
        else:
            st.warning("Nessuna segnalazione corrisponde ai filtri applicati.")
    else:
        st.warning("Nessuna segnalazione disponibile per la mappa.")

    # Mostra la tabella con i dati filtrati
    st.dataframe(filtered_df)