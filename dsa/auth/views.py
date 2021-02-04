
import functools

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from dsa import db
from dsa.auth.models import Member, MemberRole
from dsa.auth.utils import login_required, csrf_view, render_form

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.before_app_request
def load_logged_in_member():
    """If a member id is stored in the session, load the member object from
    the database into ``g.member``."""
    member_id = session.get("member_id")
    g.user = Member.query.get(member_id) if member_id is not None else None


@bp.route("/register", methods=("GET", "POST"))
@csrf_view
def register():
    """Register a new member.
    Validates that the membername is not already taken. Hashes the
    password for security.
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."
        elif db.session.query(Member.query.filter_by(username=username).exists()).scalar():
            error = f"Member {username} is already registered."

        if error is None:
            # the name is available, create the member,
            # sign them in and take them to the home
            new_member = Member(**request.form)
            new_member.save()
            session.clear()
            sesion["member_id"] = new_member.id

            return redirect(url_for("index"))

        flash(error)

    return render_form("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
@csrf_view
def login():
    """Log in a registered member by adding the member id to the session."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        error = None
        member = Member.query.filter_by(username=username).first()

        if member is None:
            error = "Incorrect membername."
        elif not member.check_password(password):
            error = "Incorrect password."

        if error is None:
            # store the member id in a new session and return to the index
            session.clear()
            session["member_id"] = member.id
            return redirect(url_for("index"))

        flash(error)

    return render_form("auth/login.html")


@bp.route("/logout")
def logout():
    """Clear the current session, including the stored member id."""
    session.clear()
    return redirect(url_for("index"))
