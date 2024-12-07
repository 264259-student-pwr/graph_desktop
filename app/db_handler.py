import sqlite3

def connect_to_db(database_path):
    """Nawiązuje połączenie z bazą danych."""
    try:
        print(f"Łączenie z bazą danych: {database_path}")
        conn = sqlite3.connect(database_path)
        return conn
    except sqlite3.Error as e:
        print(f"Błąd połączenia z bazą danych: {e}")
        return None

def get_cities(conn):
    """Pobiera miasta z bazy danych."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cities")
    return cursor.fetchall()

def get_connections(conn):
    """Pobiera połączenia między miastami z bazy danych."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM connections")
    return cursor.fetchall()
