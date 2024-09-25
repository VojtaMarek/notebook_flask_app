"""
notebook_flask_app
Web application for saving notes using flask and sqlite database.
"""

from flask import Flask, render_template, request, url_for, redirect, session, flash
from functools import wraps
import sqlite3
from typing import Optional, Type

from sql import DatabaseManager, Post


app = Flask(__name__)
app.secret_key = 'set_your_own_secret_key'
app.database = 'notes.db'

db_manager = DatabaseManager()


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap


@app.route('/',  methods=['GET'])
@login_required
def home():
    posts: list[Type[Post]] = db_manager.get_posts()
    return render_template("index.html", posts=posts, error=None)


@app.route('/save',  methods=['POST'])
@login_required
def save_note():
    note_id: Optional[str] = request.form.get("id") or None
    title: Optional[str] = request.form.get("title")
    description: Optional[str] = request.form.get("post")

    posts: list[Type[Post]] = db_manager.get_posts()

    ids: set = {post.id for post in posts}
    next_id: str = str(max(ids) + 1) if ids else '1'
    note_id: str = str(next_id) if not note_id else note_id

    if note_id.startswith("-") or note_id == '0':
        error = 'Please enter a positive Id number.'
    elif int(note_id) in ids:
        post = next((post for post in posts if post.id == int(note_id)), None)
        if post and title == post.title and description == post.description:
            error = 'No changes detected. Please make some changes to update the note.'
        else:
            db_manager.update_post(Post(int(note_id), title, description))
            return redirect(url_for('home'))
    else:
        db_manager.inser_post(Post(int(note_id), title, description))
        return redirect(url_for('home'))

    return render_template("index.html", posts=posts, error=error)


@login_required
@app.route('/delete/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    """Delete note by note_id"""
    try:
        msg: str = db_manager.delete_post(note_id)
        flash(msg)
    except Exception as e:
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


if __name__ == '__main__':
    app.run(debug=True)

