import math
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


def to_float(text):
    """Form text to float, or None if it is not a finite number."""
    try:
        value = float(text)
    except (TypeError, ValueError):
        return None
    return value if math.isfinite(value) else None


def attempt(action):
    """Run action(), flash its message or its error, and say whether it worked."""
    try:
        message = action()
    except HANDLED_ERRORS as error:
        flash(str(error), "error")
        return False
    flash(message, "success")
    return True


def build_bill(month, strategy_key):
    """Return (strategy_key, bill lines); an unknown key falls back to per_meal."""
    registry = services().strategies
    if strategy_key not in registry:
        flash("Unknown billing strategy", "error")
        strategy_key = "per_meal"
    lines = services().billing.generate_bill(month, registry[strategy_key]())
    return strategy_key, lines


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


# ---- expenses ----

@bp.get("/expenses")
def expenses_page():
    month = month_from_url()
    return render_template(
        "expenses.html",
        month=month,
        expenses=services().expenses.list_for_month(month),
        total=services().expenses.total_for_month(month),
        today=date.today().isoformat(),
    )


@bp.post("/expenses")
def add_expense():
    form = request.form
    expense_date = form.get("expense_date", "")

    def add():
        services().expenses.add_expense(
            expense_date, form.get("description", ""), to_float(form.get("amount"))
        )
        return "Expense added"

    if attempt(add):
        return redirect(url_for("web.expenses_page", month=expense_date[:7]))
    return redirect(url_for("web.expenses_page"))


# ---- billing ----

@bp.get("/billing")
def billing_page():
    month = month_from_url()
    strategy_key, lines = build_bill(month, request.args.get("strategy", "per_meal"))
    rows = [
        {
            "line": line,
            "paid": services().payments.total_paid(line.member_id, month),
            "due": services().payments.due_for(line.member_id, month, line.charge),
        }
        for line in lines
    ]
    total = round(sum(line.charge for line in lines), 2)
    return render_template(
        "billing.html", month=month, strategy=strategy_key, rows=rows, total=total
    )


@bp.post("/billing/notify")
def notify_bill():
    month = request.form.get("month", "")
    strategy_key = request.form.get("strategy", "per_meal")

    def notify():
        _, lines = build_bill(check_month(month), strategy_key)
        sent = services().notifications.send_bill_notices(month, lines)
        return f"Sent {sent} bill notices"

    attempt(notify)
    return redirect(url_for("web.billing_page", month=month, strategy=strategy_key))


# ---- payments ----

@bp.get("/payments")
def payments_page():
    month = month_from_url()
    members = services().members.list_members()
    names = {member.id: member.name for member in members}
    return render_template(
        "payments.html",
        month=month,
        members=members,
        names=names,
        payments=services().payments.list_for_month(month),
    )


@bp.post("/payments")
def add_payment():
    form = request.form
    month = form.get("month", "")

    def pay():
        payment = services().payments.pay(
            to_int(form.get("member_id")), month, to_float(form.get("amount"))
        )
        return f"Payment recorded (ref {payment.reference})"

    if attempt(pay):
        return redirect(url_for("web.payments_page", month=month))
    return redirect(url_for("web.payments_page"))
