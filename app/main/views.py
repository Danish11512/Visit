from app import app
from flask import Flask, render_template, redirect, url_for, flash
from .forms import CheckinForm


@app.route('/')
@app.route('/index')
def index():
    form = CheckinForm()
    return render_template('index.html', form=form)


# @app.route('/login')
# def login():
#     return render_template('login.html')

# @app.route('/signup')
# def signup():
#     return render_template('signup.html')

# @app.route('/dashboard')
# def dashboard():
#     return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)