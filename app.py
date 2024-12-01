import streamlit as st
import json
from utils import *
from ai import enhance_text_with_ai

# Inizializza lo stato della sessione
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}

# Mostra barra di progressione
st.title("💡 UrbanAIdea")
steps = ["Dati Utente", "Segnalazione Problema", "Riepilogo"]
st.progress((st.session_state.step - 1) / (len(steps) - 1))
st.subheader(
    f"Passo {st.session_state.step}: {steps[st.session_state.step - 1]}")

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
                st.error("La descrizione deve contenere almeno 10 caratteri.")
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
            st.success("Segnalazione inviata con successo!")
            if st.button("Nuova Segnalazione"):
                st.session_state.step = 1
                st.session_state.user_data = {}
                st.rerun()
