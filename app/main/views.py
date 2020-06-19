from . import main
from flask import Flask, render_template, redirect, url_for, flash,request
from .forms import CheckinForm
from flask_login import login_required
from ..decorators import admin_required
from sqlalchemy.orm import sessionmaker
from .. import db
from app.utils import eval_request_bool
from ..models import User

@main.route('/')
@main.route('/index', methods=["GET", "POST"])
def index():
    form = CheckinForm()

    if form.validate_on_submit():
        return render_template('main/checkin.html', fname=form.first_name.data, lname=form.last_name.data)

    return render_template('main/index.html', form=form)
@main.route("/edit_user_list", methods=["GET", "POST"])
@login_required
def user_list_page():
    """
    Renders a page with the list of users on it and related data on them. Also includes edit button to direct to
    edit user page
    :return: user_list.html which lists all the users in the application
    """

    Session = sessionmaker(bind=db.engine)
    session = Session()
    active = eval_request_bool(request.args.get("active", "true"), True)
    list_of_users = []
    list_of_users_all = User.query.filter_by(is_active=active).all()

    if request.method == "GET":
        entry = request.args.get("search_input", "")
        search_result_email = User.query.filter(
            User.email.ilike("%" + entry + "%")
        ).all()
        search_result_fname = User.query.filter(
            User.first_name.ilike("%" + entry.title() + "%")
        ).all()
        search_result_lname = User.query.filter(
            User.last_name.ilike("%" + entry.title() + "%")
        ).all()

        if not entry:
            list_of_users = list_of_users_all
        else:
            list_of_users = list(
                set(
                    search_result_email
                    + search_result_fname
                    + search_result_lname
                )
            )

    if not list_of_users:
        flash("No results found", category="error")
    # Pass in separate list of users with and without divisions
    return render_template(
        "main/user_list.html",
        list_of_users=list_of_users,
        active_users=active,
    )

if __name__ == '__main__':
    app.run(debug=True)