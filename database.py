import sqlite3
from datetime import datetime

def get_conn():
    conn = sqlite3.connect('discodatabase.db')
    cur = conn.cursor()
    return conn, cur

def check_user(username_id):
    t = (username_id, )
    conn, cur = get_conn()
    cur.execute("SELECT COUNT(*) FROM users WHERE username = ?",t)
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
    t = (user_id,)
    cur.execute("SELECT * FROM users WHERE user_id=?", t)
    row = cur.fetchone()
    if row is not None and row[1] != new_username:
        t = (new_username, user_id,)
        cur.execute("UPDATE users SET username=? WHERE user_id=?", t)
        conn.commit()
        return True
    elif row is not None:
        return False
    else:
        return None
   
def db_register_update_profile_link(user_id, new_profile_link):
    conn, cur = get_conn()
    t = (user_id,)
    result = cur.execute("SELECT * FROM users WHERE user_id=?", t)
    row = result.fetchone()
    if row is not None and row[3] != new_profile_link:
        t = (new_profile_link, user_id,)
        result = cur.execute("UPDATE users SET roblox_profile=? WHERE user_id=?", t)
        conn.commit()
        return True
    elif row is not None:
        return False
    else:
        return None

def db_register_remove_user(user_id):
    conn, cur = get_conn()
    t = (user_id, )
    result = cur.execute("DELETE FROM users WHERE user_id = ?", t)
    conn.commit()
    if result.rowcount > 0:
        return True
    else:
        return False

def db_register_view(user):
    conn, cur = get_conn()
    t = (user,)
    result = cur.execute("SELECT * FROM users WHERE user_id=?", t)
    row = result.fetchone()
    if row is not None:
        return (True, row[1], row[2], row[3])
    else:
        return (False,)

def db_register_purge():
    conn, cur = get_conn()
    result = cur.execute("DELETE FROM users")
    conn.commit()
    if result.rowcount > 0:
        return True, result
    else:
        return False, result




## POINTS ##
def remove_points(username_id, points):
    conn, cur = get_conn()
    result = db_register_view(username_id)
    if result[0]:
        booleg, username, user_id, roblox_profile = result
        t = (points, username_id, )
        t2 = (username_id, )
        cur.execute("UPDATE users SET points = points - ? WHERE user_id = ?", t)
        cur.execute("UPDATE users SET points = 0 WHERE user_id = ? AND points < 0", t2)
        conn.commit()
        return True
    else:
        return False

def add_points(username_id, points):
    conn, cur = get_conn()
    result = db_register_view(username_id)
    if result[0]:
        booleg, username, user_id, roblox_profile = result
        t = (points, username_id, )
        cur.execute("UPDATE users SET points = points + ? WHERE user_id = ?", t)
        conn.commit()
        return True
    else:
        return False

def get_user_point(username_id):
    conn, cur = get_conn()
    t = (username_id, )
    cur.execute("SELECT * FROM users WHERE user_id = ?", t)
    data = cur.fetchall()
    if not data:
        return False
    else:
        return data[0][4]
    

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
def update_quota(start, end, block):
    conn, cur = get_conn()
    cur.execute("SELECT * FROM quota_table")
    data = cur.fetchall()
    if len(data) == 0:
        cur.execute("INSERT INTO quota_table (start, end, block) VALUES (?,?,?)", (start, end, block))
    else:
        cur.execute("UPDATE quota_table SET start=?, end=?, block=?", (start, end, block))
    conn.commit()

def get_quota():
    conn, cur = get_conn()
    cur.execute("SELECT * FROM quota_table")
    data = cur.fetchall()
    return data[0][1], data[0][2], data[0][3]
    
def get_users(page = 1):
    page_offset = (page - 1) * 10
    conn, cur = get_conn()
    cur.execute("SELECT * FROM users ORDER BY points DESC LIMIT "+ str(page_offset) +",10")
    rows = cur.fetchall()
    return rows
    
    
## REQUESTS ##
def insert_points_requests(message_id, users, points, approved, created_by):
    conn, cur = get_conn()
    t = (message_id, users, points, approved, created_by, )
    cur.execute("INSERT INTO points_requests(message_id, users, points, approved, created_by)  VALUES(?,?,?,?,?)", t)
    conn.commit()
   
def check_requests(message_id):
    conn, cur = get_conn()
    t = (message_id, )
    cur.execute("SELECT * FROM points_requests WHERE message_id = ? AND approved = 0 LIMIT 1", t)
    data = cur.fetchall()
    if(not data):
        return None
    else:
        return True
       
def get_users_requests(message_id):
    conn, cur = get_conn()
    t = (message_id, )
    cur.execute("SELECT * FROM points_requests WHERE message_id = ? LIMIT 1", t)
    data = cur.fetchall()
    if(not data):
        return None
    else:
        return data[0][2], data[0][3]
        
def update_requests(message_id, app):
    conn, cur = get_conn()
    t = (app, message_id, )
    cur.execute("UPDATE points_requests SET approved = ? WHERE message_id = ?", t)
    conn.commit()
    
## POINT DATABASE ## 
async def reset_points():
    conn, cur = get_conn()
    try:
        cur.execute(f"UPDATE users SET points = 0")
        conn.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
        return False



