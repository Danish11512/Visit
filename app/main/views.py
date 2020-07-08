from . import main
from flask import Flask, render_template, redirect, url_for, flash, current_app
from .forms import CheckinForm, CheckoutForm, AppointmentForm
from ..models import Appointment
from datetime import datetime
from app import db
from config import checkin


@main.route('/', methods=["GET", "POST"])
@main.route('/index', methods=["GET", "POST"])
def index():
    form = AppointmentForm()

    
# Things to flesh out: 
# 1. Date must be today after current time or after today 
# 2. Time must be after current time and check to see if there is a appointment for that time on that day, if success send email saying appointment sent for approval. and add appointment to db

    if form.validate_on_submit():
    # Date must be today after current time or after today 
        if form.date.data.strftime("%Y-%m-%d") > datetime.now.strftime("%Y-%m-%d"):
            # create object
            pass
        if form.date.data.strftime("%Y-%m-%d") == datetime.now.strftime("%Y-%m-%d"):
            if form.time.data > datetime.now().time:
            #create pbject
                pass
        return redirect(url_for('main.index'))    
    else:
        'hi'
    return render_template('main/index.html', form=form)


@main.route('/check_in', methods=["GET", "POST"])
def check_in():
    # Check if the user exists in the db, if they don't then flash tat they don't
    form = CheckinForm()
    now = datetime.now()

    if form.validate_on_submit():
        current_app.logger.info("Form Validated")  
        
        guest = Appointment.query.filter_by(email=form.email.data,  date=now.strftime("%b %d, %Y")).first()

        if guest:
            # If the guest exist, check if they have an appointment today, if they do then check them in otherwise flash a message
            if  guest.checkin == 0:
                # check guest in if they have an appointment of the same day 
                guest.check_in = checkin["Guest Checked In"]
                db.session.add(guest)
                db.session.commit()
                current_app.logger.info("Guest Checked In")
                return render_template('main/confirm_checkin.html', fname=form.first_name.data, lname=form.last_name.data)
            else:
                # don't change anything and redirect to check in form
                current_app.logger.info("Guest checked in status is not 0, so proabably already check in")
                flash('It seems like you have already checked in', category='error')
                return redirect(url_for('main.check_in'))
        else:
            current_app.logger.info("Guest doesn't exist for today")
            # if guest doesn't exist then tell them they don't have an appointment
            flash('It looks like you don\'t have an appointment today', category='error')
            return redirect(url_for('main.check_in'))

    return render_template('main/check_in.html', form=form)

    
@main.route('/check_out', methods=["GET", "POST"])
def check_out():

    form = CheckoutForm()
    now = datetime.now()


    if form.validate_on_submit():
        current_app.logger.info("Form Validated")  
        #  If the user exists in the appointments table as checked in, check them out
        guest = Appointment.query.filter_by(email=form.email.data,  date=now.strftime("%b %d, %Y")).first()

        if guest:
             # If the guest exist, check if they had an appointment today, if they do then check them out otherwise flash a message
            if  guest.checkin == 1:
                # check guest out if they have an appointment of the same day and check in 
                guest.check_in = checkin["Guest Checked Out"]
                db.session.add(guest)
                db.session.commit()
                current_app.logger.info("Guest Checked Out")
                return render_template('main/confirm_checkout.html', fname=form.first_name.data, lname=form.last_name.data)
            else:
                # don't change anything and redirect to check in form
                current_app.logger.info("Guest checked out status is not 0, so proabably already check out or never checked in ")
                flash('It seems like you have not checked in yet', category='error')
                return redirect(url_for('main.check_in'))
        else:
            current_app.logger.info("Guest doesn't exist for today")
            # if guest doesn't exist then tell them they don't have an appointment
            flash('It looks like you didn\'t have an appointment today', category='error')
            return redirect(url_for('main.check_in'))
    
    return render_template('main/check_out.html', form=form)

    
    

if __name__ == '__main__':
    app.run(debug=True)