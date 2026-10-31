from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

from app.errors import NotFoundError, PaymentFailedError, ValidationError

bp = Blueprint("web", __name__, template_folder="templates")
HANDLED_ERRORS = (ValidationError, NotFoundError, PaymentFailedError)


def services():
    return current_app.extensions["services"]


def attempt(action):
    """Run action(), flash its message or its error, and say whether it worked."""
    try:
        message = action()
    except HANDLED_ERRORS as error:
        flash(str(error), "error")
        return False
    flash(message, "success")
    return True


@bp.get("/")
def home():
    return redirect(url_for("web.members_page"))


# ---- members ----

@bp.get("/members")
def members_page():
    return render_template("members.html", members=services().members.list_members())


@bp.post("/members")
def add_member():
    form = request.form

    def register():
        member = services().members.register(
            form.get("name", ""), form.get("room", ""), form.get("phone", "")
        )
        return f"Added {member.name}"

    attempt(register)
    return redirect(url_for("web.members_page"))


@bp.post("/members/<int:member_id>/deactivate")
def deactivate_member(member_id):
    def deactivate():
        services().members.deactivate(member_id)
        return "Member deactivated"

    attempt(deactivate)
    return redirect(url_for("web.members_page"))
