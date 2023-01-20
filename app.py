"""
notebook_flask_app
Web application for saveing notes using flask and sqlite database.
"""

from flask import Flask, render_template, request, url_for, redirect, session, flash, g
from functools import wraps
import sqlite3


app =  Flask(__name__)
app.secret_key = 'set_your_own_secret_key'
app.database = "notes.db"


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap


@app.route('/',  methods=['GET', 'POST'])
@login_required
def home():
    g.db = connect_db()
    cur = g.db.execute('SELECT * FROM posts')

    posts = [dict(id=row[0], title=row[1], description=row[2]) for row in cur.fetchall()]
    g.db.close()
    error, sql_command = "", ""
    id_is_positive = True

    if request.method == 'POST':
        id = request.form.get("id")
        title = request.form.get("title")
        description = request.form.get("post")

        next_id_str = str(len(posts)+1)
        if not id: id = next_id_str

        if id.startswith("-") or id == "0":
            id_is_positive = False
        elif int(id) >= int(next_id_str):
            sql_command = "INSERT INTO posts (title, description) VALUES(:title, :description)"
        elif int(id) > int(next_id_str):
            id = next_id_str
        else:
            sql_command = "UPDATE posts SET title=:title, description=:description WHERE id=:id"
            

        if not id_is_positive:
            error = "Please enter a positive Id number."
        elif not title or not description:
            error = "Before adding or changing a note, enter the Title and add the Content!"
        elif sql_command:
            with sqlite3.connect("notes.db") as connection:
                c = connection.cursor()
                c.execute(sql_command, {"id": id, "title": title, "description": description})
            flash(f"A note with Id {id or next_id_str} has been added/editted.") # use SQL insted of len(posts)+1; c.execute('SELECT MAX(id) FROM posts')
            return redirect(url_for('home'))            

    return render_template("index.html", posts=posts, error=error)


@app.route('/welcome')
def welcome():
    return render_template("welcome.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
            flash("Use (admin:admin) to log in.") # delete before deploying
        else:
            session['logged_in'] = True
            flash("You are just logged in!")
            return redirect(url_for('home'))
    return render_template('login.html', error=error)


@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash("You are just logged out.")
    return redirect(url_for('welcome'))


def connect_db():
    return sqlite3.connect(app.database)


if __name__ == '__main__':
    app.run(debug=True)

