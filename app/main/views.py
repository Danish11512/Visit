from . import main
from flask import Flask, render_template, redirect, url_for, flash,request, current_app
from .forms import CheckinForm, CheckoutForm, AppointmentForm, CancelForm
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
            
            if appointments and any(appointment.check_in_state < 3 for appointment in appointments):
                # If an appointment exists and is not cancelled flash check if it has already happened, if not then flash and move on
                current_app.logger.info("Appointment already exists and not cancelled") 
                flash("The date and time you have chosen is already taken, please choose another one", category="error")
                return redirect(url_for('main.index')) 
            else:
                # if there is no appoinmtent make object and flash 
                app = Appointment(
                    check_in_state = 0,
                    datetime = form_datetime,
                    first_name = form.first_name.data,
                    last_name = form.last_name.data,
                    email = form.email.data,
                    department = form.department.data,
                    description = form.description.data
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

        # Get guest object, check if the gest has already been checked in 
        guests = Appointment.query.filter_by(email=form.email.data, check_in_state=1).all()

        if guests:
             # If the guest exist, check if they had an appointment today, if they do then check them out otherwise flash a message
            for guest in guests:
                if guest.datetime.date() != datetime.now().date():
                    guests.remove(guest)

            if guests:
                guests.sort(key=lambda x: x.datetime, reverse=False)
                # If there is a guest then check them in, if there's more than one only check in the earliest one
                guest = guests[0]
                guest.check_in_state = checkin["Guest Checked Out"]
                db.session.add(guest)
                db.session.commit()
                send_email(to=form.email.data, 
                subject= "Check Out Confirmed", 
                template="main/email/check_out", 
                first_name=guest.first_name, 
                department=guest.department, 
                date=datetime.strftime(datetime.now(), "%B %d, %Y"))
                current_app.logger.info("Guest Checked Out")
                return render_template('main/confirm_checkout.html', fname=guest.first_name, lname=guest.last_name)
            else: 
                flash('It seems like you didn\'t have an apppointment today', category='error')
                current_app.logger.info("Guest doesn\'t have an appointment today")
                return redirect(url_for('main.check_in'))
        else:
            # don't change anything and redirect to check in form
            current_app.logger.info("Guest checked out status is not 0, so proabably already check out or never checked in ")
            flash('It seems like you have not checked in yet or don\'t have an appointment today', category='error')
            return redirect(url_for('main.check_in'))

           
    
    return render_template('main/check_out.html', form=form)



@main.route('/cancel_appointment', methods=["GET", "POST"])
def cancel_appointment():
    form = CancelForm()

    if form.validate_on_submit():
        form_datetime = datetime.combine(form.date.data, form.time.data)
    # Check if there's an appointment that is check_in_state of 0 ( no checked in ) with the given date, department and email
        guest = Appointment.query.filter_by(email=form.email.data, department=form.department.data, datetime= form_datetime).first()
        if guest:
            if guest.check_in_state == 0:
                # if checkin state is 0 checnge it to 3 and flash and redirect
                guest.check_in_state = checkin["Appointment Cancelled"]
                db.session.add(guest)
                db.session.commit()
                send_email(to=form.email.data, 
                subject= "Cancellation Confirmed", 
                template="main/email/cancel", 
                first_name=guest.first_name, 
                department=guest.department, 
                date=datetime.strftime(form_datetime, "%B %d, %Y"), 
                time=datetime.strftime(form_datetime, "%I:%M %p"))

                current_app.logger.info("Appointment Cancelled")
                flash("Your appointment for {} on {} with {} Department was cancelled".format(form.time.data, form.date.data, form.department.data))
                return redirect(url_for('main.cancel_appointment'))
            elif guest.check_in_state == 1 or guest.check_in_state == 2:
                # appointmetn exsits but the guest has already checkin/checked out so nothing changes, flash and redirect
                flash("Looks like you have already visited so the appointment cannot be cancelled")
                current_app.logger.info("Appointment is already checked in or check out")
                return redirect(url_for('main.cancel_appointment'))
            else:
                # The only other option is that the Appointment has already been cancelled
                flash("Looks like your appointment has already been cancelled")
                current_app.logger.info("Appointment is already cancelled")
                return redirect(url_for('main.cancel_appointment'))
        # say that the appointment doesn't exists andredirect
        
    return render_template('main/cancel_appointment.html', form=form)




if __name__ == '__main__':
    app.run(debug=True)