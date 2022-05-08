import os
import psycopg2
from helper import serialize as s

class Database:
    def __init__(self):
        url = os.environ["DATABASE_URL"]
        self.conn = psycopg2.connect(url, sslmode="require")

        # local copy so we don't need to send a query every time we just want to read something
        self.local = self.query_all()

    def set(self, key, value, serialize=True):
        cur = self.conn.cursor()

        if serialize:
            v = s.serialize(value)
        else:
            v = value

        self.local[key] = v
        cur.execute("""
            insert into egg (key, value) values (%s, %s)
            on conflict(key) do
            update set value=%s
        """, (key, v, v))

        self.conn.commit()

    def get(self, key, deserialize=True):
        if key not in self.local:
            raise KeyError(f"{key} not in database")

        v = self.local[key]
        if deserialize:
            return s.deserialize(v[0])
        return v[0]

    def __setitem__(self, key, value):
        self.set(key, value)

    def __getitem__(self, key):
        return self.get(key)

    def __delitem__(self, key):
        cur = self.conn.cursor()

        del self.local[key]
        cur.execute("delete from egg where key=%s", (key,))

    def __iter__(self):
        return self.keys()

    def __len__(self):
        return len(self.local)

    def __contains__(self, key):
        return key in self.local

    def prefix(self, pref):
        return sorted([k for k in self.local.keys() if k.startswith(pref)])
    
    def keys(self):
        return self.prefix("")

    def query_all(self):
        cur = self.conn.cursor()
        cur.execute("select * from egg")
        return dict(cur.fetchall())

    def all(self):
        return self.local

db = Database()
