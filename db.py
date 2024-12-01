import streamlit as st
import pandas as pd
import sqlite3


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
    required_columns = [
        'Geo Point', 'Nome', 'Quartiere', 'Zona di prossimità', 'Tag',
        'Descrizione'
    ]
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
        cursor.execute(insert_query,
                       (coordinates, name, district, zone, tag, description))

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
    df_display = df.drop(columns=["id", "coordinates", "name"])

    # Display filters for each column dynamically (excluding 'id' and 'coordinates')
    filters = {}
    for column in df_display.columns:
        unique_values = df_display[column].dropna().unique(
        )  # Get unique values for each column
        filter_widget = st.sidebar.selectbox(f"Filter by {column}",
                                             ["All"] + list(unique_values))
        filters[column] = filter_widget

    # Apply the filters to the DataFrame
    for column, filter_value in filters.items():
        if filter_value != "All":
            df_display = df_display[df_display[column] == filter_value]

    # Display the filtered DataFrame in Streamlit
    st.dataframe(df_display)



    # Funzione per inserire i dati nel database

def insert_data(data):
    conn = sqlite3.connect("reports.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO report (reporter_name, reporter_surname, reporter_email, reporter_phone, address, description, coordinates)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get("nome", ""),
        data.get("cognome", ""),
        data.get("email", ""),
        data.get("cellulare", ""),
        data.get("posizione", ""),
        data.get("descrizione", ""),
        data.get("coordinate", "")
    ))
    conn.commit()
    conn.close()