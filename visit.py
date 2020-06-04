import os

from flask_migrate import Migrate

from app import db, app, migrate
from app.models import (
    User,
    Permission,
    Password,
    ChangeLog,
    Role,
)

if os.getenv('FLASK_ENV') == 'development':
    from faker import Faker

migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(
        app=app,
        db=db,
        User=User,
        Permission=Permission,
        Password=Password,
        ChangeLog=ChangeLog,
        Role=Role,
    )


@app.cli.command("setup_db")
def setup_db():
    """Setup the database."""
    db.create_all()
    Role.insert_roles()


@app.cli.command("reset_db")
def reset_db():
    """Reset the database."""
    db.drop_all()
    db.create_all()
    Role.insert_roles()
    setup_roles()


def setup_roles():
    """Insert roles in the proper order."""
    Role.query.delete()
    user = Role(name="User", permissions=0x01, id=1)
    administrator = Role(name="Administrator", permissions=0xFF, id=2)
    db.session.add(user)
    db.session.add(administrator)
    db.session.commit()


@app.cli.command("generate_fake")
def create_dev_users():
    """Create users for development."""
    # Administrator
    faker = Faker()
    first_name = faker.first_name()
    last_name = faker.last_name()
    administrator = User(
        email="{first_initial}{last_name}@{email_domain}".format(
            first_initial=first_name[0].lower(),
            last_name=last_name.lower(),
            email_domain=app.config["EMAIL_DOMAIN"],
        ),
        first_name=first_name,
        last_name=last_name,
        password_hash="Change4me",
        role=Role.query.filter_by(name="Administrator").first()
    )
    db.session.add(administrator)
    administrator.password_list.update(administrator.password_hash)


    # Users
    for i in range(10):
        first_name = faker.first_name()
        last_name = faker.last_name()
        user = User(
            email="{first_initial}{last_name}@{email_domain}".format(
                first_initial=first_name[0].lower(),
                last_name=last_name.lower(),
                email_domain=app.config["EMAIL_DOMAIN"],
            ),
            first_name=first_name,
            last_name=last_name,
            password_hash="Change4me",
            role=Role.query.filter_by(name="User").first()
        )
        db.session.add(user)
        user.password_list.update(user.password_hash)

    db.session.commit()
