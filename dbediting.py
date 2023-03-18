from Functions.dbFunctions import *

def create_table():
    conn, cur = get_conn()
    cur.execute('''CREATE TABLE IF NOT EXISTS point_requests (
                    message_id TEXT,
                    created_by TEXT,
                    amount INTEGER,
                    approved INTEGER,
                    approved_by TEXT
                );''')

    conn.commit()
    print("Made table")

def delete_table(table):
    conn, cur = get_conn()
    cur.execute(f"DROP TABLE {table}")
    conn.commit()
    print(f"Deleted {table}")

def edit_table(table, new_colum, new_column_type):
    conn, cur = get_conn()
    cur.execute(f"ALTER TABLE {table} ADD COLUMN {new_colum} {new_column_type}")
    conn.commit()
    print("Added colum")

def rename_colum():
    conn, cur = get_conn()
    cur.execute("ALTER TABLE users RENAME COLUMN username TO user_id")
    conn.commit()
    print("Renamed colum")

def remove_column(table_name, column_name):
    conn, cur = get_conn()
    cur.execute(f"PRAGMA foreign_keys=off;")
    cur.execute(f"ALTER TABLE {table_name} DROP COLUMN {column_name}")
    conn.commit()
    print("Removed column")

def remove_primary_column(database_name, table_name, column_name):
    conn = sqlite3.connect(database_name)
    cur = conn.cursor()
    
    cur.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in cur.fetchall() if col[1] != column_name]
    columns_str = ", ".join(columns)
    
    # Remove the primary key constraint, if it exists
    cur.execute(f"PRAGMA foreign_keys=off;")
    cur.execute(f"BEGIN TRANSACTION;")
    cur.execute(f"ALTER TABLE {table_name} RENAME TO old_{table_name};")
    cur.execute(f"CREATE TABLE {table_name} ({columns_str});")
    cur.execute(f"INSERT INTO {table_name} ({columns_str}) SELECT {columns_str} from old_{table_name};")
    cur.execute(f"DROP TABLE old_{table_name};")
    cur.execute(f"COMMIT;")
    cur.execute(f"PRAGMA foreign_keys=on;")

    conn.commit()
    conn.close()
    print("Removed column")

def swap_columns(table_name, column1, column2):
    conn, cur = get_conn()
    cur.execute(f"ALTER TABLE {table_name} RENAME COLUMN {column1} TO temp_{column1}")
    cur.execute(f"ALTER TABLE {table_name} RENAME COLUMN {column2} TO {column1}")
    cur.execute(f"ALTER TABLE {table_name} RENAME COLUMN temp_{column1} TO {column2}")
    conn.commit()
    print(f"Swapped {column1} // {column2} in {table_name}")
    
def clear_table(table):
    conn, cur = get_conn()
    result = cur.execute(f"DELETE FROM {table}")
    conn.commit()
    if result.rowcount > 0:
        print(f"Cleared {result.rowcount} rows")
    else:
        print("Failed to clear")

def reset_ids(table):
    conn, cur = get_conn()
    cur.execute(f"UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='{table}'")
    conn.commit()
    print(f"Reset the ID for table '{table}'")

def update_column_datatype(table_name, old_column_name, new_column_name, new_datatype):
    conn, cur = get_conn()
    cur.execute(f"ALTER TABLE {table_name} RENAME COLUMN {old_column_name} TO temp_column")
    cur.execute(f"ALTER TABLE {table_name} ADD COLUMN {new_column_name} {new_datatype}")
    cur.execute(f"UPDATE {table_name} SET {new_column_name} = CAST(temp_column AS {new_datatype})")
    cur.execute(f"ALTER TABLE {table_name} DROP COLUMN temp_column")
    conn.commit()
    print(f"Column {old_column_name} in table {table_name} has been successfully changed to {new_datatype} and renamed to {new_column_name}")


