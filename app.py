"""
notebook_flask_app
Web application for saving notes using flask and sqlite database.
"""

from flask import Flask, render_template, request, url_for, redirect, session, flash, g
from functools import wraps
import sqlite3
from typing import Optional


app = Flask(__name__)
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
    try:
        with sqlite3.connect("notes.db") as connection:
            c = connection.cursor()
            c.execute("SELECT * FROM posts")
            posts = [dict(id=row[0], title=row[1], description=row[2]) for row in c.fetchall()]
    except sqlite3.Error as e:
        flash(f'An error occurred while fetching notes: {e}')
        posts = []

    error: Optional[str] = None
    sql_command: Optional[str] = None

    if request.method == 'POST':
        note_id: Optional[str] = request.form.get("id") or None
        title: Optional[str] = request.form.get("title")
        description: Optional[str] = request.form.get("post")

        ids: set = {post.get('id') for post in posts}
        next_id: str = str(max(ids) + 1) if ids else '1'
        note_id: str = str(next_id) if not note_id else note_id

        if note_id.startswith("-") or note_id == '0':
            error = 'Please enter a positive Id number.'
        elif int(note_id) in ids:
            post = next((post for post in posts if post.get('id') == int(note_id)), None)
            if post and title == post.get('title') and description == post.get('description'):
                error = 'No changes detected. Please make some changes to update the note.'
            else:
                sql_command = "UPDATE posts SET title=:title, description=:description WHERE id=:id"
        else:
            sql_command = "INSERT INTO posts (title, description) VALUES(:title, :description)"

        if sql_command:
            try:
                with sqlite3.connect("notes.db") as connection:
                    c = connection.cursor()
                    c.execute(sql_command, {"id": note_id, "title": title, "description": description})
                    connection.commit()
                flash(f'A note with Id {note_id} has been added/editted.')
                return redirect(url_for('home'))
            except sqlite3.Error as e:
                error = f'An error occurred while adding/editing the note: {e}'

    return render_template("index.html", posts=posts, error=error)


@login_required
@app.route('/delete/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    """Delete note by note_id"""
    try:
        with sqlite3.connect("notes.db") as connection:
            c = connection.cursor()
            c.execute("DELETE FROM posts WHERE id=:id", {"id": note_id})
            connection.commit()
        flash(f'Note with ID {note_id} has been deleted')
    except sqlite3.Error as e:
        flash(f'An error occurred while deleting the note: {e}')
    return redirect(url_for('home'))


@app.route('/welcome')
def welcome():
    return render_template("welcome.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
            flash('Use (admin:admin) to log in.')  # delete before deploying
        else:
            session['logged_in'] = True
            flash('You are just logged in!')
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

