
# this file has functions that talk to the database

import mysql.connector
import db_config

# connect to the database
def get_connection():
    return mysql.connector.connect(
        host=db_config.host,
        user=db_config.user,
        password=db_config.password,
        database=db_config.database
    )

# add into the shopping list
def add_item(name, quantity):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO shopping_list (name, quantity) VALUES (%s, %s)", (name, quantity))
    conn.commit()
    conn.close()

# show items
def view_items():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM shopping_list")
    rows = cur.fetchall()
    conn.close()
    return rows

# delete a item
def delete_item(item_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM shopping_list WHERE id = %s", (item_id,))
    conn.commit()
    conn.close()
