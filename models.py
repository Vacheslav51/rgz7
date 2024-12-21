from database import get_db_connection

def create_user(username):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (username) VALUES (%s) RETURNING id;", (username,))
    user_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return user_id

def create_subscription(name, amount, frequency, start_date, user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO subscriptions (name, amount, frequency, start_date, user_id)
        VALUES (%s, %s, %s, %s, %s) RETURNING id;
    """, (name, amount, frequency, start_date, user_id))
    subscription_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return subscription_id

def get_subscriptions(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM subscriptions WHERE user_id = %s;", (user_id,))
    subscriptions = cur.fetchall()
    cur.close()
    conn.close()
    return subscriptions

def update_subscription(subscription_id, amount=None, frequency=None, start_date=None):
    conn = get_db_connection()
    cur = conn.cursor()
    
    if amount is not None:
        cur.execute("UPDATE subscriptions SET amount = %s WHERE id = %s;", (amount, subscription_id))
    
    if frequency is not None:
        cur.execute("UPDATE subscriptions SET frequency = %s WHERE id = %s;", (frequency, subscription_id))

    if start_date is not None:
        cur.execute("UPDATE subscriptions SET start_date = %s WHERE id = %s;", (start_date, subscription_id))
    
    conn.commit()
    cur.close()
    conn.close()

def delete_subscription(subscription_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM subscriptions WHERE id = %s;", (subscription_id,))
    conn.commit()
    cur.close()
    conn.close()
