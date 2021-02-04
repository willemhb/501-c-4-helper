from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from dsa import db
from dsa.auth.models import Member
from dsa.auth.util import login_required, role_required, csrf_view, render_form


bp = Blueprint("website", __name__)


@bp.route("/")
def index():
    """
    Show the homepage.
    """
    return render_template("website/index.html")


@bp.route("/about")
def about():
    """
    Show the about page.
    """
    return render_template("website/about.html")


@bp.route("/<int:member_id>", methods=("GET","POST"))
@login_required
@csrf_view
def home(member_id):
    """
    Shows the member panel.
    """
    member = Member.get_or_404(member_id)


@bp.route("/admin")
@role_required("administrator")
def admin():
    """
    Render the admin panel.
    """
    return render_template("admin/main.html")
