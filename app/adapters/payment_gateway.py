import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass

FAILING_WALLET = "01000000000"  # demo wallet that always has no balance


@dataclass
class PaymentResult:
    success: bool
    reference: str = ""
    message: str = ""


class PaymentGateway(ABC):
    """What our business code needs from any payment provider."""

    @abstractmethod
    def charge(self, phone: str, amount: float) -> PaymentResult:
        """Take `amount` from the wallet of `phone`."""


class SandboxWalletClient:
    """Pretend third-party wallet SDK. Works offline so demos need no network."""

    def make_payment(self, wallet_no: str, amount: str) -> dict:
        if float(amount) <= 0:
            return {"status": "FAILED", "error": "Invalid amount"}
        if wallet_no == FAILING_WALLET:
            return {"status": "FAILED", "error": "Insufficient balance"}
        return {"status": "COMPLETED", "trxID": "SBX" + uuid.uuid4().hex[:8].upper()}


class WalletGatewayAdapter(PaymentGateway):
    """Adapter: turns the wallet SDK's calls and dicts into our PaymentGateway interface."""

    def __init__(self, client):
        self.client = client

    def charge(self, phone: str, amount: float) -> PaymentResult:
        response = self.client.make_payment(wallet_no=phone, amount=f"{amount:.2f}")
        if response.get("status") == "COMPLETED":
            return PaymentResult(True, reference=response["trxID"])
        return PaymentResult(False, message=response.get("error", "Payment failed"))
