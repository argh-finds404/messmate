from datetime import date

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

from app.errors import NotFoundError, PaymentFailedError, ValidationError
from app.validation import check_month

bp = Blueprint("web", __name__, template_folder="templates")
HANDLED_ERRORS = (ValidationError, NotFoundError, PaymentFailedError)


def services():
    return current_app.extensions["services"]


def current_month():
    return date.today().strftime("%Y-%m")


def month_from_url():
    """Read ?month=; on a bad value show an error and use the current month."""
    month = request.args.get("month") or current_month()
    try:
        return check_month(month)
    except ValidationError as error:
        flash(str(error), "error")
        return current_month()


def to_int(text):
    """Form text to int, or None if it is not a whole number."""
    try:
        return int(text)
    except (TypeError, ValueError):
        return None


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


# ---- meals ----

@bp.get("/meals")
def meals_page():
    month = month_from_url()
    members = services().members.list_members(active_only=True)
    totals = services().meals.monthly_totals(month)
    rows = [(member, totals.get(member.id, 0)) for member in members]
    return render_template(
        "meals.html", month=month, members=members, rows=rows, today=date.today().isoformat()
    )


@bp.post("/meals")
def add_meals():
    form = request.form
    meal_date = form.get("meal_date", "")

    def record():
        services().meals.record(
            to_int(form.get("member_id")), meal_date, to_int(form.get("meal_count"))
        )
        return "Meals saved"

    if attempt(record):
        return redirect(url_for("web.meals_page", month=meal_date[:7]))
    return redirect(url_for("web.meals_page"))
