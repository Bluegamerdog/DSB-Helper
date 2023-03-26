import sqlite3
import time
from datetime import datetime

def get_conn():
    conn = sqlite3.connect('database_v3.db')
    cur = conn.cursor()
    return conn, cur

def replace_value(table, column, old_value, new_value):
    conn, cur = get_conn()
    cur.execute(f"UPDATE {table} SET {column} = ? WHERE {column} = ?", (new_value, old_value))
    conn.commit()
    print(f"Replaced {old_value} with {new_value} in column {column} of {table}")


def check_user(username_id):
    t = (username_id, )
    conn, cur = get_conn()
    cur.execute("SELECT COUNT(*) FROM users WHERE user_id = ?",t)
    users = cur.fetchall()
    if(users[0][0] == 0):
        return False
    else:
        return True

## REGISTRY ##
def db_register_new(username, user_id, profile_link):
    conn, cur = get_conn()
    t = (user_id, )
    result = cur.execute("SELECT * FROM users WHERE user_id=?", t)
    if result.fetchone() is not None:
        return False
    else:
        t = (username, user_id, profile_link, 0, )
        result = cur.execute("INSERT INTO users(username, user_id, roblox_profile, points) VALUES(?,?,?,?)", t)
        conn.commit()
        return True
    
def db_register_update_username(user_id, new_username):
    conn, cur = get_conn()
    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    if row and row[0] != new_username:
        cur.execute("UPDATE users SET username=? WHERE user_id=?", (new_username, user_id))
        conn.commit()
        return True
    else:
        return False
   
def db_register_update_profile_link(user_id, new_profile_link):
    conn, cur = get_conn()
    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    if row and row[2] != new_profile_link:
        cur.execute("UPDATE users SET roblox_profile=? WHERE user_id=?", (new_profile_link, user_id))
        conn.commit()
        return True
    else:
        return False

def db_register_remove_user(user_id):
    conn, cur = get_conn()
    t = (user_id, )
    result = cur.execute("SELECT * FROM users WHERE user_id=?", t)
    if result.fetchone() is None:
        return False
    else:
        cur.execute("DELETE FROM users WHERE user_id = ?", t)
        conn.commit()
        return True

def db_get_all_data():
    conn, cur = get_conn()
    cur.execute("SELECT * FROM users")
    rows = cur.fetchall()
    return rows

def db_register_get_data(user_id):
    conn, cur = get_conn()
    t = (user_id,)
    cur.execute("SELECT * FROM users WHERE user_id=?", t)
    user_data = cur.fetchone()
    if user_data == None:
        return False
    else:
        return user_data

def db_register_purge():
    conn, cur = get_conn()
    result = cur.execute("DELETE FROM users")
    conn.commit()
    if result.rowcount > 0:
        return True, result
    else:
        return False, result


## POINTS ##
def remove_points(user_id, points):
    conn, cur = get_conn()
    result = db_register_get_data(user_id)
    if result[1]:
        t = (points, result[1], )
        t2 = (result[1], )
        cur.execute("UPDATE users SET points = points - ? WHERE user_id = ?", t)
        cur.execute("UPDATE users SET points = 0 WHERE user_id = ? AND points < 0", t2)
        conn.commit()
        return True
    else:
        return False

def add_points(user_id, points):
    conn, cur = get_conn()
    result = db_register_get_data(user_id)
    if result:
        t = (points, result[1], )
        cur.execute("UPDATE users SET points = points + ? WHERE user_id = ?", t)
        conn.commit()
        return True
    else:
        return False

def get_points(user_id):
    conn, cur = get_conn()
    result = db_register_get_data(user_id)
    if result:
        t = (user_id, )
        cur.execute("SELECT * FROM users WHERE user_id = ?", t)
        data = cur.fetchall()
        return int(data[0][3]) if data else 0
    else:
        return False

def get_users_amount(page = 1):
    page_offset = (page - 1) * 10
    conn, cur = get_conn()
    cur.execute("SELECT * FROM users ORDER BY points DESC LIMIT "+ str(page_offset) +",10")
    rows = cur.fetchall()
    return rows

def get_total_points():
    conn, cur = get_conn()
    cur.execute("SELECT SUM(points) FROM users")
    total_points = cur.fetchone()[0]
    return total_points


async def reset_points():
    conn, cur = get_conn()
    try:
        cur.execute("UPDATE users SET points = 0, days_onloa = NULL")
        conn.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
        return False


def set_days_onloa(user_id, days):
    conn, cur = get_conn()
    result = db_register_get_data(user_id)
    if result:
        if days == 0:
            cur.execute("UPDATE users SET days_onloa = NULL WHERE user_id = ?", (result[1],))
        elif days is not None:
            cur.execute("UPDATE users SET days_onloa = ? WHERE user_id = ?", (days, result[1]))
        conn.commit()
        return True
    else:
        return False

## LEADERBOARD ##
def add_leaderboard(username, message_id, count):
    conn, cur = get_conn()
    now=datetime.now()
    timestamp=datetime.timestamp(now)
    t = (username, message_id, timestamp, 1, count, )
    cur.execute("INSERT INTO board_tables(username, message_id, created_time, page_number, last_usernumber) VALUES(?,?,?,?,?)", t)
    conn.commit()
    
def check_leaderboard(message_id, user_id):
    conn, cur = get_conn()
    t = (user_id, message_id, )
    cur.execute("SELECT COUNT(*) FROM board_tables WHERE username = ? AND message_id = ?",t)
    data = cur.fetchall()
    if(data[0][0] == 0):
        return False
    else:
        return True
  
def get_leaderboard_page(message_id):
    conn, cur = get_conn()
    t = (message_id, )
    cur.execute("SELECT * FROM board_tables WHERE message_id = ?",t)
    data = cur.fetchall()
    return data[0][4], data[0][5]
    
def update_leaderboard(page, last_user, message_id):
    conn, cur = get_conn()
    t = (page, last_user, message_id)
    cur.execute("UPDATE board_tables SET page_number = ? , last_usernumber = ? WHERE message_id = ?", t)
    conn.commit()

## QUOTA ##

def update_quota(start=None, end=None, block=None):
    conn, cur = get_conn()
    cur.execute("SELECT * FROM quota_table")
    data = cur.fetchall()
    if len(data) == 0:
        if start == None or end == None or block == None:
            return False # If there is no existing quota information, you have to provide all three values.
        else:
            cur.execute("INSERT INTO quota_table (start, end, block) VALUES (?,?,?)", (start, end, block))
    else:
        updated = 0
        if start is not None:
            cur.execute("UPDATE quota_table SET start=?", (start,))
            if cur.rowcount > 0:
                updated += 1
        if end is not None:
            cur.execute("UPDATE quota_table SET end=?", (end,))
            if cur.rowcount > 0:
                updated += 1
        if block is not None:
            cur.execute("UPDATE quota_table SET block=?", (block,))
            if cur.rowcount > 0:
                updated += 1
        if updated >= 1:
            conn.commit()
            return updated
        else:
            return False
            
    conn.commit()

def get_quota():
    conn, cur = get_conn()
    cur.execute("SELECT * FROM quota_table")
    data = cur.fetchall()
    return data[0][1], data[0][2], data[0][3]
    
## OPERATIONS ##

def get_roblox_link(user_id):
    conn, cur = get_conn()
    t = (user_id,)
    cur.execute("SELECT * FROM users WHERE user_id=?", t)
    result = cur.fetchone()
    if result:
        return result[2]
    else:
        return None
    
def op_create_scheduled(op_type, op_pal, op_start, op_trello, op_message_id):
    conn, cur = get_conn()
    t = (op_type, op_pal, op_start, op_trello, 0, 0, op_message_id, )
    cur.execute("INSERT INTO op_table (OP_TYPE, OP_PAL, OP_START, OP_TRELLO, OP_SPON, OP_CONCLU, OP_MESSAGE_ID) VALUES (?,?,?,?,?,?,?)", t)
    conn.commit()
    print("Operation created successfully.")

def op_get_info(op_pal):
    conn, cur = get_conn()
    t = (op_pal,)
    cur.execute("SELECT * FROM op_table WHERE OP_PAL=?", t)
    result = cur.fetchone()
    if result is None:
        print("Cannot find operation.")
        return
    return result

def op_create_spontaneous(op_type, op_pal, op_message_id, op_trello=None):
    conn, cur = get_conn()
    op_start = int(time.time())
    if op_trello==None:
        op_trello = "TBA"
    t = (op_type, op_pal, op_start, op_trello, 1, 0, op_message_id, )
    cur.execute("INSERT INTO op_table (OP_TYPE, OP_PAL, OP_START, OP_TRELLO, OP_SPON, OP_CONCLU, OP_MESSAGE_ID) VALUES (?,?,?,?,?,?,?)", t)
    conn.commit()
    print("Operation created successfully.")

def op_cancel(op_pal):
    conn, cur = get_conn()
    t = (op_pal,)
    cur.execute("DELETE FROM op_table WHERE OP_PAL=?", t)
    conn.commit()
    return True

def op_conclude(op_pal):
    conn, cur = get_conn()
    t = (op_pal,)
    cur.execute("UPDATE op_table SET OP_CONCLU=1 WHERE OP_PAL=?", t)
    rows_affected = cur.rowcount
    conn.commit()
    if rows_affected == 0:
        return False
    else:
        return True

def op_edit(op_pal, op_type=None, op_start=None, op_trello=None):
    conn, cur = get_conn()
    updates = []
    if op_type is not None:
        updates.append("OP_TYPE=?")
    if op_start is not None:
        updates.append("OP_START=?")
    if op_trello is not None:
        updates.append("OP_TRELLO=?")

    if updates:
        t = (op_pal,) + tuple(
            value for value in (op_type, op_start, op_trello) if value is not None
        )
        query = f"UPDATE op_table SET {','.join(updates)} WHERE OP_PAL=?"
        cur.execute(query, t)
        conn.commit()
        print("Operation edited successfully.")
    else:
        print("Cannot find operation")

    
    

