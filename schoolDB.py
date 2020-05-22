# Week 12, Assignment 13
# By: Joshua Rifkin

import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from contextlib import closing

app = Flask(__name__)
app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'hw13.db'),
    SECRET_KEY=os.urandom(24),
    USERNAME='admin',
    PASSWORD='password'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'db'):
        g.db = connect_db()
    return g.db


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.before_request
def before_request():
    """Opens the database at the beginning of the request"""
    g.db = connect_db()


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'db'):
        g.db.close()


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You\'ve been logged in successfully.')
            return redirect(url_for('dashboard'))
    return render_template('login.html', error=error)


@app.route('/dashboard', methods=['GET'])
def dashboard():
    db = get_db()
    studs = db.execute('SELECT ID, firstName, lastName FROM students').fetchall()
    quizzes = db.execute('SELECT ID, subject, questions, quizDate FROM quizzes').fetchall()

    return render_template('dashboard.html', students=studs, quizzes=quizzes)


@app.route('/student/add', methods=['GET', 'POST'])
def addStudent():
    if not session.get('logged_in'):
        abort(401)
    if request.method == 'GET':
        return render_template('addstudent.html')
    elif request.method == 'POST':
        try:
            db = get_db()
            db.execute('INSERT INTO students (firstName, lastName) values (?, ?)',
                       [request.form['first'], request.form['last']])
            db.commit()
        except Exception:
            flash('Student Was Not Added Successfully, Please Try Again.')
            return render_template('addstudent.html')

    flash('New Student Was Successfully Added')
    return redirect(url_for('dashboard'))

    # TODO figure out how to catch an invalid entry/if entry fails.


@app.route('/quiz/add', methods=['GET', 'POST'])
def addQuiz():
    if not session.get('logged_in'):
        abort(401)
    if request.method == 'GET':
        return render_template('addquiz.html')
    elif request.method == 'POST':
        db = get_db()
        db.execute('INSERT INTO quizzes (subject, questions, quizDate) values (?, ?, ?)',
                   [request.form['subject'], request.form['questions'], request.form['date']])
        db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('dashboard'))


@app.route('/student/<studID>', methods=['GET'])
def displayResults(studID):
    if not session.get('logged_in'):
        abort(401)
    message = None
    db = get_db()
    student = db.execute('SELECT * FROM students WHERE ID = ?', studID).fetchone()
    results = db.execute("""
    SELECT quizID, grade, quizzes.subject, quizzes.questions, quizzes.quizDate
    FROM grades
    JOIN quizzes ON quizID = quizzes.ID
    WHERE studID = ?
    """, studID).fetchall()
    if not results:
        message = "No Quiz Results Available."

    return render_template('grades.html', student=student, results=results, message=message)


@app.route('/results/add', methods=['GET', 'POST'])
def addResult():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    if request.method == 'GET':
        students = db.execute('SELECT * FROM students').fetchall()
        quizzes = db.execute('SELECT * FROM quizzes').fetchall()
        return render_template('addresults.html', students=students, quizzes=quizzes)
    elif request.method == 'POST':
        db.execute('INSERT INTO grades (studID, quizID, grade) VALUES (?, ?, ?)', [request.form['student'],
                                                                                   request.form['quiz'],
                                                                                   request.form['grade']])
        db.commit()
        flash("New Grade Results Added Successfully.")
        return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    session.pop('loggedIn', None)
    flash('You\'ve been logged out successfully.')
    return redirect(url_for('login'))


if __name__ == '__main__':
    init_db()
    app.run()
