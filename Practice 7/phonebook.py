import csv
from connect import conn, cur
 
 
def create_table():
    cur.execute("""
    CREATE TABLE IF NOT EXISTS phonebook (
        id SERIAL PRIMARY KEY,
        name TEXT,
        phone TEXT
    );
    """)
    conn.commit()
 
 
def insert_user(name, phone):
    cur.execute(
        "INSERT INTO phonebook (name, phone) VALUES (%s, %s)",
        (name, phone)
    )
    conn.commit()
 
 
def insert_from_csv(filename):
    with open(filename, "r", newline="") as f:
        reader = csv.reader(f)
        next(reader)  # skip header row
        for row in reader:
            cur.execute(
                "INSERT INTO phonebook (name, phone) VALUES (%s, %s)",
                (row[0], row[1])
            )
    conn.commit()
    print("CSV loaded!")
 
 
def show_all():
    cur.execute("SELECT * FROM phonebook")
    rows = cur.fetchall()
    if rows:
        for r in rows:
            print(r)
    else:
        print("Phonebook is empty.")
 
 
def search_by_name(name):
    # search by name (case-insensitive)
    cur.execute("SELECT * FROM phonebook WHERE name ILIKE %s", (f"%{name}%",))
    rows = cur.fetchall()
    if rows:
        for r in rows:
            print(r)
    else:
        print("No contacts found.")
 
 
def search_by_phone(prefix):
    # search by phone prefix
    cur.execute("SELECT * FROM phonebook WHERE phone LIKE %s", (prefix + "%",))
    rows = cur.fetchall()
    if rows:
        for r in rows:
            print(r)
    else:
        print("No contacts found.")
 
 
def update_user(name, new_name=None, new_phone=None):
    if new_name:
        cur.execute("UPDATE phonebook SET name=%s WHERE name=%s", (new_name, name))
    if new_phone:
        cur.execute("UPDATE phonebook SET phone=%s WHERE name=%s", (new_phone, name))
    conn.commit()
    print("Contact updated.")
 
 
def delete_user(name=None, phone=None):
    if name:
        cur.execute("DELETE FROM phonebook WHERE name=%s", (name,))
    elif phone:
        cur.execute("DELETE FROM phonebook WHERE phone=%s", (phone,))
    conn.commit()
    print("Contact deleted.")
 
 
# create table on startup
create_table()
 
while True:
    print("\n1. Add contact")
    print("2. Show all")
    print("3. Search")
    print("4. Update contact")
    print("5. Delete contact")
    print("6. Exit")
    print("7. Load CSV")
    choice = input(">> ")
 
    if choice == "1":
        name = input("Name: ")
        phone = input("Phone: ")
        insert_user(name, phone)
 
    elif choice == "2":
        show_all()
 
    elif choice == "3":
        t = input("Search by: 1-name  2-phone: ")
        if t == "1":
            search_by_name(input("Name: "))
        else:
            search_by_phone(input("Phone prefix: "))
 
    elif choice == "4":
        name = input("Whose contact to update: ")
        new_name = input("New name (press Enter to skip): ")
        new_phone = input("New phone (press Enter to skip): ")
        update_user(name, new_name or None, new_phone or None)
 
    elif choice == "5":
        t = input("Delete by: 1-name  2-phone: ")
        if t == "1":
            delete_user(name=input("Name: "))
        else:
            delete_user(phone=input("Phone: "))
 
    elif choice == "6":
        break
 
    elif choice == "7":
        insert_from_csv("contacts.csv")
 
cur.close()
conn.close()