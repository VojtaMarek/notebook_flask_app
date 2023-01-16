import sqlite3

with sqlite3.connect("notes.db") as connection:
    c = connection.cursor()
    c.execute("CREATE TABLE posts(id INTEGER PRIMARY KEY, title TEXT, description TEXT)")
    # c.execute('INSERT INTO posts VALUES("0", "note title", "note content")')
    # c.execute('CREATE INDEX "" ON "posts" ("id")')
