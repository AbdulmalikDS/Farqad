import sqlite3
import os
from tabulate import tabulate

def print_table_data(conn, table_name):
    """Print all data from a table."""
    cursor = conn.cursor()
    
    # Get column names
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = [column[1] for column in cursor.fetchall()]
    
    # Get all data
    cursor.execute(f"SELECT * FROM {table_name};")
    rows = cursor.fetchall()
    
    if not rows:
        print(f"Table '{table_name}' exists but contains no data.\n")
        return
    
    print(f"Data in table '{table_name}' ({len(rows)} rows):")
    print(tabulate(rows, headers=columns, tablefmt="grid"))
    print("\n")

# Try both potential locations
db_paths = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "front-end", "data", "sqlite.db"),
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sqlite.db"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "front-end", "sqlite.db")
]

for db_path in db_paths:
    if os.path.exists(db_path):
        print(f"\n=== Database: {db_path} ===")
        try:
            # Connect to the database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get all table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            if not tables:
                print("No tables found in this database.")
            else:
                print(f"Tables found: {len(tables)}")
                
                for i, table in enumerate(tables, 1):
                    table_name = table[0]
                    print(f"\n{i}. {table_name}")
                    
                    # Get table schema
                    cursor.execute(f"PRAGMA table_info({table_name});")
                    schema = cursor.fetchall()
                    
                    schema_data = []
                    for col in schema:
                        schema_data.append([col[1], col[2], "PRIMARY KEY" if col[5] == 1 else ""])
                    
                    print("\nTable Structure:")
                    print(tabulate(schema_data, headers=["Column", "Type", "Constraint"], tablefmt="grid"))
                    
                    # Get and print actual data rows
                    print_table_data(conn, table_name)
            
            conn.close()
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
    else:
        print(f"Database file not found: {db_path}")

if __name__ == "__main__":
    print("Database Viewer Utility")
    print("=======================")
    print("Checking for databases in project...") 