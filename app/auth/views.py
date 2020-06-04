from . import auth
from flask import Flask, render_template, redirect, url_for, flash
from .forms import LoginForm


@auth.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():               
        return redirect(url_for('auth.login'))

    return render_template('auth/login.html', form=form)


# @app.route('/signup')
# def signup():
#     return render_template('signup.html')

# @app.route('/dashboard')
# def dashboard():
#     return render_template('dashboard.html')

if __name__ == '__auth__':
    app.run(debug=True)
