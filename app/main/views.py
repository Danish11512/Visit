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
# 2. Time must be after current time and check to see if there is a appointment for that time on that day, if success send email saying appointment sent for approval. and add appointment to db

    if form.validate_on_submit():
        current_app.logger.info("Form Validated")  
    # Creating datetime object to use
        form_datetime = datetime.combine(form.date.data, form.time.data)
        now_datetime = datetime.now()
        
        # If date is today's or more than today's check if time is taken and create object, otherwise flash to chose another time 
        if form_datetime.date() <= now_datetime.date():
            current_app.logger.info("Dates checked, checking time")  
            appointment = Appointment.query.filter_by(datetime=form_datetime).all()
            
            if appointment:
                # If an appointment exists flash and move on
                current_app.logger.info("Appointment already exists") 
                flash("The date and time you have chosen is already taken, please choose another one", category="error")
            
            elif form_datetime.time() <= now_datetime.time():
                # See if there is an appointment for that time or chosen time is before current time, flash a message
                current_app.logger.info("Time taken") 
                flash("The time you have chosen is taken, please change your time", category="error")
            else:
                # if there is no appoinment make object and flash 
                app = Appointment(
                    check_in = 0,
                    datetime = form_datetime,
                    first_name = form.first_name.data,
                    last_name = form.last_name.data,
                    email = form.email.data,
                    department = form.department.data
                
                )
                db.session.add(app)
                db.session.commit()
                flash('Appointment created, wating for approval', category='success')
                current_app.logger.info("Appointment Created") 
                return redirect(url_for('main.index'))    
        else:
            # if date is before today's flash to choose anoher date
            current_app.logger.info("Current Date is taken")
            flash("The date you have chosen is before the current date, please change your date", category="error")
        
        
        return redirect(url_for('main.index'))    
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