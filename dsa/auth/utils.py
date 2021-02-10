from flask import g, current_app, redirect, abort, render_template, request, session
from functools import wraps
from secrets import token_urlsafe, compare_digest
from hashlib import sha256
import hmac


def csrf_view(view):
    """
    Wraps views that send and process forms.
    
    If the request method is 'GET', generates a CSRF token and saves it in the session.
    
    If the request method is 'POST', it gets the hidden "csrf_token" form input and compares it
    against the saved token. If the saved token matches the token in the form, it calls the wrapped view
    function. Otherwise, it aborts with a 403 status code.

    Before returning, it deletes the "csrf_token" key from the session to prevent leakage.
    """
    @wraps(view)
    def wrapper(*args,**kwargs):
        if request.method == "GET":
            session["csrf_token"] = token_urlsafe(32)
            return view(*args,**kwargs)

        else:
            form_tok = request.form["csrf_token"]
            sess_tok = session["csrf_token"]

            if compare_digest(form_tok,hmac.digest(g.config["SECRET_KEY"],sha256)):
                del session["csrf_token"]
                return view(*args,**kwargs)

            else:
                return abort(403)

    return wrapper


def render_form(tplt, **ctx):
    """
    Adds csrf token to the rendering context.
    """
    t = hmac.digest(g.config["SECRET_KEY"],session["csrf_token"],sha256)
    return render_template(tplt, csrf_token=t, **ctx)



def login_required(view):
    """
    View decorator that redirects anonymous members to the login page.
    """
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.member is None:
            flash("You must be logged in to view this content.")
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


def role_required(role:str):
    """
    View decorator that guards based on a member's privileges.
    """
    def decorator(view):
        @wraps(view)
        def wrapper(**kwargs):
            if g.member is None:
                # permissions imply being logged in
                flash("You must be logged in to view this content.")
                return redirect(url_for("auth.login"))

            elif not g.member.has_role(role):
                flash("You do not have permission to view that page.")
                return redirect(url_for("website.index"))

            else:
                return view(**kwargs)

        return wrapper
    return decorator
