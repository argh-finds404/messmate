from types import SimpleNamespace

from app.adapters.notifiers import SandboxSmsClient
from app.adapters.payment_gateway import SandboxWalletClient, WalletGatewayAdapter
from app.repositories.expense_repository import ExpenseRepository
from app.repositories.meal_repository import MealRepository
from app.repositories.member_repository import MemberRepository
from app.repositories.payment_repository import PaymentRepository
from app.services.billing_service import BillingService
from app.services.billing_strategies import EqualSplitStrategy, PerMealRateStrategy
from app.services.expense_service import ExpenseService
from app.services.meal_service import MealService
from app.services.member_service import MemberService
from app.services.notification_service import NotificationService
from app.services.notifier_factory import NotifierFactory
from app.services.payment_service import PaymentService


def build_gateway(mode):
    """Pick the payment gateway named in the config."""
    if mode == "sandbox":
        return WalletGatewayAdapter(SandboxWalletClient())
    raise ValueError(f"Unknown payment mode: {mode}")


def build_services(config, conn):
    """Create repositories and services and connect them to each other."""
    member_repo = MemberRepository(conn)
    meal_repo = MealRepository(conn)
    expense_repo = ExpenseRepository(conn)
    payment_repo = PaymentRepository(conn)
    gateway = build_gateway(config["PAYMENT_MODE"])
    notifier = NotifierFactory.create(config["NOTIFY_CHANNEL"], sms_client=SandboxSmsClient())
    return SimpleNamespace(
        members=MemberService(member_repo),
        meals=MealService(meal_repo, member_repo),
        expenses=ExpenseService(expense_repo),
        billing=BillingService(member_repo, meal_repo, expense_repo),
        payments=PaymentService(payment_repo, member_repo, gateway),
        notifications=NotificationService(member_repo, notifier),
        # To add a billing rule: write a BillingStrategy subclass and add one line here.
        strategies={"per_meal": PerMealRateStrategy, "equal": EqualSplitStrategy},
    )
