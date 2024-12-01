import streamlit as st
import re


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
    labels = [
        label for keyword, label in keywords.items()
        if keyword in description_lower
    ]
    return labels if labels else ["indefinito"]


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
