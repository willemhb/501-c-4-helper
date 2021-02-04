import os

from dotenv import dotenv_values
import click
from pathlib import Path
from flask import Flask
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(test_config=None):
    """
    Set up the application instance.
    """
    app = Flask(__name__,instance_relative_config=True)
    config = dotenv_values(".env")
    app.config.from_mapping(
        **config,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    db.init_app(app)

    app.cli.add_command(init_db_command)
    app.cli.add_command(create_admin_command)

    from dsa import auth, website

    app.register_blueprint(auth.bp)
    app.register_blueprint(website.bp)

    app.add_url_rule("/", endpoint="index")

    return app


def init_db():
    """
    Database setup.
    """
    db.drop_all()
    db.create_all()


def create_admin(username, password, email):
    """
    Create a new user with admin privileges.
    """
    try:
        from .auth.models import Member, MemberRole
        new_member = Member(username=username, email=email, password=password)
        new_member.save()
        admin_role = MemberRole(role="administrator",member_id=new_member.id)
        db.session.add(admin_role)
        db.session.commit()
        return None

    except Exception as e:
        return str(e)


@click.command("create-admin")
@click.option("--username", default="admin", help="Username for admin account.")
@click.option("--password", default="admin", help="Password for admin account.")
@click.argument("email")
@with_appcontext
def create_admin_command(username, password, email):
    if (rslt := create_admin(username, password, email)) is not None:
        click.echo(f"Something went wrong: {rslt}.")

    else:
        click.echo("Admin account created.")


@click.command("init-db")
@with_appcontext
def init_db_command():
    init_db()
    click.echo("Database initialized.")
