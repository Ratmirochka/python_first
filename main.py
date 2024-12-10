from bd_query import DbQuery
from flask import Flask, render_template, url_for, request, flash, redirect, session, abort
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kjh92JHGkj023Kfewi43KJKfgew'

@app.route('/', methods=['GET', 'POST'])
def login():
    if 'userLogged' in session:
        return redirect(url_for('profile', username=session['userLogged']))
    elif request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        result = DbQuery.is_corect(username, password)
        if result == True:
            flash('Logged in successfully !', category='success')
            session['userLogged'] = username
            return redirect(url_for('profile', username=session['userLogged']))
        elif result == False:
            flash('Incorrect username / password !', category='error')
        elif result == None:
            flash('Can not connect to database')
    return render_template('login.html', title="Авторизация")

@app.route('/logout')
def logout():
    if 'userLogged' in session:
        session.pop('userLogged')
    session.clear()
    return redirect(url_for('login'))

@app.errorhandler(404)
def pageNotFount(error):
    return render_template('page404.html'), 404

@app.route("/profile/<username>")
def profile(username):
    if 'userLogged' not in session or session['userLogged'] != username:
        abort(401)
    return render_template('profile.html', username=username)

