import streamlit as st
import json
from utils import *
from ai import enhance_text_with_ai
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
page = st.sidebar.radio("Seleziona una pagina", ["Informazioni", "Segnalazione", "Gestione Segnalazioni"])

if page == "Informazioni":
    # Static Page Content
    st.title("📄 Informazioni su UrbanAIdea")
    st.write("""
    UrbanAIdea è un'iniziativa innovativa che utilizza l'intelligenza artificiale 
    per migliorare la gestione delle segnalazioni urbane. Questa piattaforma consente:

    - Raccolta dei dati utente in modo semplice e sicuro.
    - Miglioramento automatico delle descrizioni tramite AI.
    - Generazione di riepiloghi completi per la revisione.

    Grazie alla tecnologia AI, puntiamo a migliorare la qualità della vita urbana e 
    a rendere le città più intelligenti e sostenibili.
    """)

    st.image("https://via.placeholder.com/800x400", caption="Smart City powered by AI")
    st.write("Per tornare all'applicazione principale, usa la barra laterale.")
elif page == "Segnalazione":
    # Main App Flow
    # Mostra barra di progressione
    st.title("📄 Segnalazione")
    steps = ["Dati Utente", "Segnalazione Problema", "Riepilogo"]
    st.progress((st.session_state.step - 1) / (len(steps) - 1))
    st.subheader(f"Passo {st.session_state.step}: {steps[st.session_state.step - 1]}")

    # Step 1: Dati utente
    if st.session_state.step == 1:
        nome = st.text_input("Nome", st.session_state.user_data.get('nome', ''))
        cognome = st.text_input("Cognome",
                                st.session_state.user_data.get('cognome', ''))
        email = st.text_input("Email", st.session_state.user_data.get('email', ''))
        cellulare = st.text_input("Cellulare",
                                  st.session_state.user_data.get('cellulare', ''))

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
        posizione = st.text_input("Posizione/Via del problema",
                                  st.session_state.user_data.get('posizione', ''))

        if 'descrizione' not in st.session_state.user_data:
            st.session_state.user_data['descrizione'] = ""
        descrizione = st.text_area("Descrizione del problema",
                                   st.session_state.user_data['descrizione'])

        if st.button("✨ Migliora con l'AI"):
            st.session_state.user_data['descrizione'] = enhance_text_with_ai(descrizione)
            st.rerun()

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Indietro"):
                prev_step()
        with col2:
            if st.button("Avanti"):
                if not posizione:
                    st.error("La posizione del problema è obbligatoria.")
                elif len(descrizione) < 10:
                    st.error("La descrizione deve contenere almeno 10 caratteri.")
                else:
                    st.session_state.user_data.update({
                        "posizione": posizione,
                        "descrizione": st.session_state.user_data['descrizione']
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
                st.success("Segnalazione inviata con successo!")
                if st.button("Nuova Segnalazione"):
                    st.session_state.step = 1
                    st.session_state.user_data = {}
                    st.rerun()
elif page == "Gestione Segnalazioni":
    st.title("📄 Gestione segnalazioni su UrbanAIdea")

    # Add a map with Folium
    st.subheader("🌍 Mappa delle segnalazioni")
    m = folium.Map(location=[41.9028, 12.4964], zoom_start=12)  # Rome, Italy as default location

    # Example markers
    folium.Marker(
        location=[41.9028, 12.4964],
        popup="Segnalazione 1: Problema al lampione",
        tooltip="Clicca per dettagli",
    ).add_to(m)

    folium.Marker(
        location=[41.8902, 12.4922],
        popup="Segnalazione 2: Rifiuti abbandonati",
        tooltip="Clicca per dettagli",
        icon=folium.Icon(color="red"),
    ).add_to(m)

    # Example heatmap data (list of [latitude, longitude])
    heat_data = [
        [41.9028, 12.4964],  # Location 1
        [41.8902, 12.4922],  # Location 2
        [41.9055, 12.5014],  # Location 3
        [41.8919, 12.5113],  # Location 4
    ]

    # Add heatmap layer
    HeatMap(heat_data).add_to(m)

    # Render the map in Streamlit
    st_map = st_folium(m, width=800, height=500)