# Visit - A Checkin/Checkout System for customers. 

The Visit app let's people to make and cancel appointments to NYC Department of Records. An NYC Department of Records employee can then view these appointements, other employees, accept and reject these appoitments and customize their account. This allows a holistic view of all appointments, users, visitors, and faculty.

## Installation 
After you have cloned the repo you need to set it up, this app usese PostgreSQL, but you can use anything as long as you change the database link in the config file.

### 1. Setup pipenv
For this app pipenv is important because many of the cli commands made for this app run best with it. Using pipenv setup a shell and instal lthe dependencies in the pipfile
``` 
pipenv shell
pipenv install 
```
now that you're in the shell with everything installed we need to export some variables to make everything work
```
export FLASK_ENV=development
export FLASK_APP=visit.py
``` 
### 2. DB Setup
If you are using postgres, create a db called visit_dev or change the link in the config.py file. If you don't have postgres, change the link in the config.py file to your db link.

### 3. Setting up Users
You can run your app right now but you don't have a schema or anyway to store any data. So the best way to do that is to first create a schema and visit.py has a function to do that for you. Make sure you are in the pipenv shell. 
```
run flask reset_db
```
To get fake users do 
```
run flask generate_fake
``` 
### 4. Email
To setup the email system you need to export some variables according to your email provider, I am using an smtp server.
```
export MAIL_SERVER="<smtp server address>"
export MAIL_PORT=<smtp port>
export MAIL_USERNAME="<username>"
export MAIL_PASSWORD="<password>"
export MAIL_SUBJECT_PREFIX="[Visit]"
export MAIL_DEFAULT_SENDER=(“Records Visit” , “appdev@records.nyc.gov”)
```
### 5. Final
That's it! now that you're done just do  
```
flask run 
``` 
to run , if you are trying to log in, the default password set for the randomly generated users is **Change4me**, after logging in the first time it will prompt you to change the password. That's all there is to it! Have Fun!




