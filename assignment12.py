"""Assignement 12"""

import sqlite3
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, render_template, flash

DATABASE = 'hw12.db'
DEBUG = True
SECRET_KEY = '8\x00xqN\xbd\x85\xa6B<\x88\xc2c\xb4\xb84A\x02\x96\xd4\xe9\x0c\x03\x1c'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)


def connect_db():
    """Connects to database"""
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    """creates the database for app"""
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.before_request
def before_request():
    """initializes connection to database"""
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    """ends connection to database"""
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.route('/')
def main_page():
    """main page of app"""
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """allows uers to login"""
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        if request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You have been logged in')
            return redirect(url_for('dashboard'))
    else:
        return render_template('login.html', error=error)


@app.route('/dashboard', methods=['GET'])
def dashboard():
    """loads the dashboard"""
    cur1 = g.db.execute('SELECT id, first_name, last_name from STUDENTS ORDER BY id ASC')
    students = [dict(stud_id=row[0], first_name=row[1],
                     last_name=row[2]) for row in cur1.fetchall()]
    cur2 = g.db.execute('SELECT id, subject, num_questions, date from QUIZZES ORDER BY id ASC')
    quizzes = [dict(quiz_id=row[0], subject=row[1], num_quest=row[2],
                    date=row[3]) for row in cur2.fetchall()]
    return render_template('dashboard.html', students=students, quizzes=quizzes)


@app.route('/student/add', methods=['GET', 'POST'])
def add_student():
    """adds a student"""
    if request.method == 'GET':
        return render_template('addstudent.html')
    if request.method == 'POST':
        if not session.get('logged_in'):
            return redirect('/login')
        try:
            g.db.execute('INSERT INTO STUDENTS (first_name, last_name) VALUES (?,?)',
                         (request.form['first_name'].title(), request.form['last_name'].title()))
            g.db.commit()
            flash('Student was successfully added')
            return redirect('/dashboard')
        except:
            flash("Somthing went wrong! Student not added.")
            return redirect('/student/add')


@app.route('/quiz/add', methods=['GET', 'POST'])
def add_quiz():
    """adds a quiz"""
    if request.method == 'GET':
        return render_template('addquiz.html')
    if request.method == 'POST':
        if not session.get('logged_in'):
            return redirect('/login')
        try:
            g.db.execute('INSERT INTO QUIZZES (subject, num_questions, date) VALUES (?,?,?)',
                         (request.form['subject'].title(), request.form['num_questions'],
                          request.form['date']))
            g.db.commit()
            flash('Quiz was successfully added')
            return redirect('/dashboard')
        except:
            flash("Somthing went wrong! Quiz not added.")
            return redirect('/quiz/add')


@app.route('/student/<id_num>', methods=['GET'])
def show_results(id_num):
    """displays the scores for a student"""
    cur3 = g.db.execute('SELECT first_name, last_name from STUDENTS WHERE id=?', (id_num))
    name = cur3.fetchall()[0]
    student_name = '{} {}'.format(name[0], name[1])
    cur4 = g.db.execute('SELECT quiz_id, score from RESULTS WHERE student_id=?', (id_num))
    quiz_results = [dict(quiz_id=row[0], score=row[1]) for row in cur4.fetchall()]
    return render_template('results.html', results=quiz_results, student_name=student_name)


@app.route('/results/add', methods=['GET', 'POST'])
def add_results():
    """adds quiz results"""
    if request.method == 'GET':
        # cur5 = g.db.execute('SELECT id, subject from QUIZZES')
        # quizzes = [dict(id=row[0], subject=row[1]) for row in cur5.fetchall()]
        # cur6 = g.db.execute('SELECT id, first_name, last_name from STUDENTS')
        # students = [dict(id=row, name='{}{}'.format(row[0], row[1])) for row in cur6.fetchall()]
        return render_template('addresults.html')
    if request.method == 'POST':
        try:
            g.db.execute('INSERT INTO RESULTS (student_id, quiz_id, score) VALUES (?,?,?)',
                         (request.form['student_id'], request.form['quiz_id'],
                          request.form['score']))
            g.db.commit()
            flash('Quiz Result was added')
            return redirect('/dashboard')
        except:
            flash("Something went wrong! Result not added.")
            return redirect('/results/add')


@app.route('/logout')
def logout():
    """logs the user out"""
    session.pop('logged_in', None)
    return redirect('/login')


if __name__ == '__main__':
    app.run()
