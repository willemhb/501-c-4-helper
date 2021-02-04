from flask import g, current_app, redirect, abort, render_template, request, session
from functools import wraps
from secrets import token_urlsafe, compare_digest


def csrf_view(view):
    """
    Wraps views that send and process forms with .
    """
    @wraps(view)
    def wrapper(*args,**kwargs):
        if request.method == "GET":
            session["csrf_token"] = token_urlsafe(32)
            return view(*args,**kwargs)

        else:
            form_tok = request.form["csrf_token"]
            sess_tok = session["csrf_token"]

            if compare_digest(form_tok,sess_tok):
                del session["csrf_token"]
                return view(*args,**kwargs)

            else:
                return abort(403)

    return wrapper


def render_form(tplt, **ctx):
    """
    Adds csrf token to the rendering context.
    """
    return render_template(tplt,csrf_token=session["csrf_token"],**ctx)



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
