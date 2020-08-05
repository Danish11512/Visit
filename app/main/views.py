from . import main
from flask import Flask, render_template, redirect, url_for, flash,request, current_app
from .forms import CheckinForm, CheckoutForm, AppointmentForm
from app import db
from ..models import User, Appointment
from config import checkin
from datetime import datetime
from ..email_notification import send_email


@main.route('/', methods=["GET", "POST"])
@main.route('/index', methods=["GET", "POST"])
def index():
    form = AppointmentForm()

    if form.validate_on_submit():
        current_app.logger.info("Form Validated")  
    # Creating datetime object to use
        form_datetime = datetime.combine(form.date.data, form.time.data)
        now_datetime = datetime.now()
        
        # If date is today's or more than today's check if time is taken and create object, otherwise flash to chose another time 
        if form_datetime.date() <= now_datetime.date():
            current_app.logger.info("Dates checked, checking time")  
            # check if there is an appointment foor that dateime and where check_in is 1 which means an appointment exist that hasn't been cancelled or completed
            appointment = Appointment.query.filter_by(datetime=form_datetime, check_in=1).all()
            
            if appointment:
                # If an appointment exists flash check if i has already happened, if not then flash and move on
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
                current_app.logger.info("Appointment Created , waiting approval")
                template = "Hi {}, you appointment has been created, it is waiting for approval".format(form.first_name.data)
                send_email(to=form.email.data, subject= "Appointment Created, Waiting Confirmation", template="main/email/new_appointment", first_name=form.first_name.data, department=form.department.data)
                current_app.logger.info("Email Sent")
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
        
        guest = Appointment.query.filter_by(email=form.email.data,  check_in=0).first()

        if guest:
            # If the guest exist, check if they have an appointment today, if they do then check them in otherwise flash a message
            if  guest.check_in == 0 and (guest.datetime.date() == datetime.now().date()):
                # check guest in if they have an appointment of the same day and are approved
                if guest.approved:
                    guest.check_in = checkin["Guest Checked In"]
                    db.session.add(guest)
                    db.session.commit()
                    current_app.logger.info("Guest Checked In")
                    return render_template('main/confirm_checkin.html', fname=form.first_name.data, lname=form.last_name.data)
                else:
                    current_app.logger.info("Guest was not approved, not checking in")
                    flash('I looks like your appoinmen was not approved, please contact the administrator', category='error')
                    redirect(url_for('main.check_in'))
            else:
                # don't change anything and redirect to check in form
                if guest.check_in == 0:
                    current_app.logger.info("Guest checked in status is not 0, so proabably already checked")
                    flash('It seems like you have already checked in', category='error')
                    return redirect(url_for('main.check_in'))
                else:
                    current_app.logger.info("Guest doesn't have an appointment today")
                    flash('It seems you don\'t have an appointment today', category='error')
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

        # Get guest object
        guest = Appointment.query.filter_by(email=form.email.data, check_in=1).first()

        if guest:
             # If the guest exist, check if they had an appointment today, if they do then check them out otherwise flash a message
            if guest.datetime.date() == datetime.now().date():
                # if the dates match move on other wise flash there is no appointment today

                if  guest.check_in == 1:
                    # check guest out if they have checked in already
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
                flash('It seems like you didn\'t have an apppointment today', category='error')
                current_app.logger.info("Guest doesn\'t have an appoinment today")
                return redirect(url_for('main.check_in'))
        else:
            current_app.logger.info("Guest doesn't exist")
            # if guest doesn't exist then tell them they don't have an appointment
            flash('It looks like you didn\'t have an appointment today', category='error')
            return redirect(url_for('main.check_in'))
    
    return render_template('main/check_out.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)