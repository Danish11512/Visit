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
    
        if form_datetime > now_datetime:
            # If the date and time is more than today check if there is an appointment that already exists for that date and time
            current_app.logger.info("Date and time checked, checking existing appointments")  
            # check if there is an appointment foor that dateime and where check_in is 1 which means an appointment exist that hasn't been cancelled or completed
            appointments = Appointment.query.filter_by(datetime=form_datetime, department=form.department.data).all()
            print (appointments)
            if appointments and all(appointment.check_in_state < 4 for appointment in appointments):
                # If an appointment exists and is not cancelled flash check if it has already happened, if not then flash and move on
                current_app.logger.info("Appointment already exists and not cancelled") 
                flash("The date and time you have chosen is already taken, please choose another one", category="error")
            else:
                # if there is no appoinment make object and flash 
                app = Appointment(
                    check_in_state = 0,
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
                send_email(to=form.email.data, 
                            subject= "Appointment Created, Waiting Confirmation", 
                            template="main/email/new_appointment", 
                            first_name=form.first_name.data, 
                            department=form.department.data, 
                            date=datetime.strftime(form_datetime, "%B %d, %Y"), 
                            time=datetime.strftime(form_datetime, "%I:%M %p"))
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
        # Get all the appointmesnt that are created but not checked in or anything else
        guests = Appointment.query.filter_by(email=form.email.data,  check_in_state=0, approved=True, department=form.department.data).all()

        if not guests:
             # Take care of the flash messages for each of the conditions that could have gone wrong
            current_app.logger.info("Either the email was wrong, user was already checked in, not approved, or wrong department was chosen")
            flash("Looks like you appointment is not here, please try putting the correct information or contact the administrator")
            return redirect(url_for('main.check_in'))
        else:
            # remove all the onees that are not for today
            for guest in guests:
                if guest.datetime.date() != datetime.now().date():
                    guests.remove(guest)

        if guests:
            # sort to check in the earliest one first
            guests.sort(key=lambda x: x.datetime, reverse=False)
            # If there is a guest then check them in, if there's more than one only check in the earliest one
            guest = guests[0]
            guest.check_in_state = checkin["Guest Checked In"]
            db.session.add(guest)
            db.session.commit()
            current_app.logger.info("Guest Checked In")
            send_email(to=form.email.data, 
                subject= "Checkin Confirmed", 
                template="main/email/check_in", 
                first_name=form.first_name.data, 
                department=form.department.data, 
                date=datetime.strftime(datetime.now(), "%B %d, %Y"), 
                time=datetime.strftime(datetime.now(), "%I:%M %p"))
            return render_template('main/confirm_checkin.html', fname=form.first_name.data, lname=form.last_name.data)
        else:
            # flash that your apopintment is not today
            current_app.logger.info("The apopintment does not exist for today")
            flash("Looks like you don't have an appointment today")
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

                if  guest.check_in_state == 1:
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