import os
import psycopg2
from helper import serialize

class Database:
    def __init__(self):
        url = os.environ['DATABASE_URL']
        self.conn = psycopg2.connect(url, sslmode='require')

    def __setitem__(self, key, value):
        cur = self.conn.cursor()
        v = serialize.serialize(value)
        cur.execute("""
            insert into egg (key, value) values (%s, %s)
            on conflict(key) do
            update set value=%s
        """, (key, v, v))
        self.conn.commit()

    def __getitem__(self, key):
        cur = self.conn.cursor()
        cur.execute("select value from egg where key=%s", (key,))
        v = cur.fetchone()
        if v is None:
            raise KeyError(f"{key} not in database")
        return serialize.deserialize(v[0])

    def __delitem__(self, key):
        cur = self.conn.cursor()
        cur.execute("delete from egg where key=%s", (key,))

    def __iter__(self):
        return self.keys()

    def __len__(self):
        cur = self.conn.cursor()
        cur.execute("select count(*) from egg")
        a = cur.fetchone()
        return a[0]

    def __contains__(self, key):
        cur = self.conn.cursor()
        cur.execute("select 1 from egg where key=%s", (key,))
        a = cur.fetchone()
        return a is not None

    def prefix(self, pref):
        cur = self.conn.cursor()
        cur.execute("select key from egg where key like %s", (pref + "%",))
        return iter([x[0] for x in cur.fetchall()])
    
    def keys(self):
        return self.prefix("")

db = Database()
