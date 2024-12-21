import psycopg2

def get_db_connection():
    conn = psycopg2.connect("dbname='rgz' user='postgres' host='localhost' password='postgres'")
    return conn
