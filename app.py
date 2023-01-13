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

    posts = [dict(id=row[0], title=row[1], description=row[2]) for i,row in enumerate(cur.fetchall())]
    g.db.close()
    error, sql_command = "", ""

    if request.method == 'POST':
        id = request.form.get("id")
        title = request.form.get("title")
        description = request.form.get("post")

        if not id or id == str(len(posts)):
            sql_command = f"INSERT INTO posts VALUES('{len(posts)}','{title}', '{description}')"
        elif not id.startswith("-"):
            sql_command = f"UPDATE posts SET title='{title}', description='{description}' WHERE id={id}"
        else:
            error = "Please do not enter a negative Id."

        if sql_command and title and description:
            with sqlite3.connect("sample.db") as connection:
                c = connection.cursor()
                c.execute(sql_command)
            flash(f"A new note with Id {len(posts)} has been added.")
            return redirect(url_for('home'))
        else:
            error = "Before adding or changing a note, enter the Title and add the Content!"
        
        
    
    return render_template("index.html", posts=posts, error=error)


@app.route('/welcome')
def welcome():
    return render_template("welcome.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again. Hint: Use admin:admin to log in.'
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

