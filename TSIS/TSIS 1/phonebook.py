import csv
import json
from connect import get_connection

# ── helpers ────────

def get_conn():
    return get_connection()

def print_rows(rows):
    """Print query results in a readable way."""
    if not rows:
        print("  (no results)")
        return
    for r in rows:
        print(" ", dict(r) if hasattr(r, '_asdict') else r)

# ── CSV import ────────

def import_csv(filepath="contacts.csv"):
    """
    Import contacts from CSV.
    Calls upsert_contact procedure for each row — handles duplicates automatically.
    Expected columns: name, phone, phone_type, email, birthday, group
    """
    with get_conn() as conn, conn.cursor() as cur, open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            cur.execute(
                "CALL upsert_contact(%s, %s, %s, %s::date, %s)",
                (
                    row["name"],
                    row.get("phone") or None,
                    row.get("email") or None,
                    row.get("birthday") or None,
                    row.get("group") or "Other",
                ),
            )
            # if phone_type differs from default 'mobile', update it
            if row.get("phone") and row.get("phone_type", "mobile") != "mobile":
                cur.execute(
                    "UPDATE phones SET type=%s WHERE phone=%s",
                    (row["phone_type"], row["phone"]),
                )
            count += 1
        conn.commit()
    print(f"  Imported {count} contacts from {filepath}")

# ── JSON export / import ──────
def export_json(filepath="contacts.json"):
    """
    Export all contacts with phones and group to JSON.
    Uses a single query with LEFT JOIN to get everything at once.
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT c.name, c.email, c.birthday::text, g.name AS grp,
                   json_agg(json_build_object('phone', ph.phone, 'type', ph.type))
                       FILTER (WHERE ph.phone IS NOT NULL) AS phones
            FROM contacts c
            LEFT JOIN groups g  ON g.id = c.group_id
            LEFT JOIN phones ph ON ph.contact_id = c.id
            GROUP BY c.name, c.email, c.birthday, g.name
            ORDER BY c.name
        """)
        contacts = []
        for name, email, bday, grp, phones in cur.fetchall():
            contacts.append({
                "name": name, "email": email, "birthday": bday,
                "group": grp, "phones": phones or []
            })
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=2, ensure_ascii=False)
    print(f"  Exported {len(contacts)} contacts to {filepath}")

def import_json(filepath="contacts.json"):
    """
    Import contacts from JSON.
    On duplicate name: ask user to skip or overwrite.
    """
    with open(filepath, encoding="utf-8") as f:
        contacts = json.load(f)

    with get_conn() as conn, conn.cursor() as cur:
        for c in contacts:
            # check if contact already exists
            cur.execute("SELECT id FROM contacts WHERE name=%s", (c["name"],))
            exists = cur.fetchone()

            if exists:
                choice = input(f"  '{c['name']}' already exists. [s]kip / [o]verwrite? ").strip().lower()
                if choice != "o":
                    continue  # skip this contact

            # upsert contact (first phone only via procedure, rest added separately)
            phones = c.get("phones") or []
            first_phone = phones[0]["phone"] if phones else None
            first_type  = phones[0]["type"]  if phones else "mobile"

            cur.execute(
                "CALL upsert_contact(%s, %s, %s, %s::date, %s)",
                (c["name"], first_phone, c.get("email"), c.get("birthday"), c.get("group") or "Other"),
            )

            # add remaining phones using add_phone procedure
            for p in phones[1:]:
                try:
                    cur.execute("CALL add_phone(%s, %s, %s)", (c["name"], p["phone"], p["type"]))
                except Exception:
                    conn.rollback()

        conn.commit()
    print(f"  Imported {len(contacts)} contacts from {filepath}")

# ── filter / search / sort ─────────────────────

def filter_by_group(group_name):
    """Show contacts in a specific group."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT c.name, c.email, c.birthday, g.name AS grp,
                   string_agg(ph.phone || ' (' || ph.type || ')', ', ') AS phones
            FROM contacts c
            LEFT JOIN groups g  ON g.id = c.group_id
            LEFT JOIN phones ph ON ph.contact_id = c.id
            WHERE g.name ILIKE %s
            GROUP BY c.name, c.email, c.birthday, g.name
            ORDER BY c.name
        """, (group_name,))
        print_rows(cur.fetchall())

def search_by_email(query):
    """Partial email search — e.g. 'gmail' matches all Gmail contacts."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT name, email, birthday FROM contacts
            WHERE email ILIKE %s
            ORDER BY name
        """, (f"%{query}%",))
        print_rows(cur.fetchall())

def search_all(query):
    """
    Full search via DB function search_contacts().
    Matches name, email, or any phone number — defined in procedures.sql.
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM search_contacts(%s)", (query,))
        print_rows(cur.fetchall())

def list_sorted(sort_by="name"):
    """
    List all contacts sorted by: name | birthday | created_at (date added).
    Uses a whitelist to prevent SQL injection.
    """
    allowed = {"name": "c.name", "n": "c.name", "birthday": "c.birthday", "b": "c.birthday", "date": "c.created_at", "d": "c.created_at"}
    order = allowed.get(sort_by, "c.name")   # default to name if invalid input

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(f"""
            SELECT c.name, c.email, c.birthday, g.name AS grp,
                   string_agg(ph.phone || ' (' || ph.type || ')', ', ') AS phones
            FROM contacts c
            LEFT JOIN groups g  ON g.id = c.group_id
            LEFT JOIN phones ph ON ph.contact_id = c.id
            GROUP BY c.name, c.email, c.birthday, g.name, c.created_at
            ORDER BY {order}
        """)
        rows = cur.fetchall()
        print(f"\n  Total: {len(rows)} contacts\n")
        for r in rows:
            print(f"  Name    : {r[0]}")
            print(f"  Email   : {r[1] or '—'}")
            print(f"  Birthday: {r[2] or '—'}")
            print(f"  Group   : {r[3] or '—'}")
            print(f"  Phones  : {r[4] or '—'}")
            print(f"  {'-'*30}")

# ── paginated navigation ───────────────

def paginate(page_size=3):
    """
    Navigate contacts page by page using the DB function get_contacts_page().
    The function uses LIMIT/OFFSET — defined in procedures.sql (Practice 8).
    User types 'next', 'prev', or 'quit' to navigate.
    """
    offset = 0
    while True:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM get_contacts_page(%s, %s)", (page_size, offset))
            rows = cur.fetchall()

        if not rows and offset == 0:
            print("  No contacts found.")
            break

        print(f"\n  --- Page (offset={offset}) ---")
        print_rows(rows)

        cmd = input("  [next/prev/quit]: ").strip().lower()
        if cmd == "next" and len(rows) == page_size:
            offset += page_size
        elif cmd == "prev" and offset >= page_size:
            offset -= page_size
        elif cmd == "quit":
            break
        else:
            print("  (already at first/last page or invalid command)")

# ── stored procedure calls ──────────────────

def add_phone(name, phone, phone_type="mobile"):
    """Add a phone to existing contact via add_phone() procedure."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, phone_type))
        conn.commit()
    print(f"  Phone added to '{name}'")

def move_to_group(name, group_name):
    """Move contact to a group (creates group if not exists) via move_to_group()."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("CALL move_to_group(%s, %s)", (name, group_name))
        conn.commit()
    print(f"  '{name}' moved to group '{group_name}'")


def delete_contact(name):
    """Delete contact by name via delete_contact() procedure."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("CALL delete_contact(%s, NULL)", (name,))
        conn.commit()
    print(f"  '{name}' deleted.")

# ── console menu ────────────────────

MENU = """
======= PhoneBook =======
 1. Import CSV
 2. Export JSON
 3. Import JSON
 4. Search (name / email / phone)
 5. Filter by group
 6. Search by email
 7. Sort contacts
 8. Browse pages
 9. Add phone to contact
10. Move contact to group
11. Show all contacts
12. Delete contact
 0. Exit
========================="""

def main():
    while True:
        print(MENU)
        choice = input("Choose: ").strip()

        if choice == "1":
            path = input("  CSV file [contacts.csv]: ").strip() or "contacts.csv"
            import_csv(path)

        elif choice == "2":
            path = input("  Save to [contacts.json]: ").strip() or "contacts.json"
            export_json(path)

        elif choice == "3":
            path = input("  JSON file [contacts.json]: ").strip() or "contacts.json"
            import_json(path)

        elif choice == "4":
            q = input("  Search query: ").strip()
            search_all(q)

        elif choice == "5":
            g = input("  Group name (Family/Work/Friend/Other): ").strip()
            filter_by_group(g)

        elif choice == "6":
            q = input("  Email search (e.g. 'gmail'): ").strip()
            search_by_email(q)

        elif choice == "7":
            s = input("  Sort by [name/birthday/date]: ").strip() or "name"
            list_sorted(s)

        elif choice == "8":
            n = input("  Page size [3]: ").strip()
            paginate(int(n) if n.isdigit() else 3)

        elif choice == "9":
            name  = input("  Contact name: ").strip()
            phone = input("  Phone number: ").strip()
            ptype = input("  Type [mobile/home/work]: ").strip() or "mobile"
            add_phone(name, phone, ptype)

        elif choice == "10":
            name  = input("  Contact name: ").strip()
            group = input("  Group name: ").strip()
            move_to_group(name, group)

        elif choice == "11":
            list_sorted("name")

        elif choice == "12":
            name = input("  Contact name to delete: ").strip()
            delete_contact(name)

        elif choice == "0":
            print("  Bye!")
            break

        else:
            print("  Invalid choice.")

if __name__ == "__main__":
    main()