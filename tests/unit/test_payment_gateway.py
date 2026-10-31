from unittest.mock import Mock

import pytest

from app.adapters.payment_gateway import (
    PaymentGateway,
    PaymentResult,
    SandboxWalletClient,
    WalletGatewayAdapter,
)


def test_gateway_interface_cannot_be_instantiated():
    with pytest.raises(TypeError):
        PaymentGateway()


def test_adapter_is_a_payment_gateway():
    assert isinstance(WalletGatewayAdapter(Mock()), PaymentGateway)


def test_adapter_translates_success():
    client = Mock()
    client.make_payment.return_value = {"status": "COMPLETED", "trxID": "TX123"}
    result = WalletGatewayAdapter(client).charge("01711111111", 1500.5)
    assert result == PaymentResult(True, reference="TX123")
    client.make_payment.assert_called_once_with(wallet_no="01711111111", amount="1500.50")


def test_adapter_translates_failure_with_message():
    client = Mock()
    client.make_payment.return_value = {"status": "FAILED", "error": "Insufficient balance"}
    result = WalletGatewayAdapter(client).charge("01711111111", 100)
    assert result == PaymentResult(False, reference="", message="Insufficient balance")


def test_adapter_uses_default_message_when_sdk_gives_none():
    client = Mock()
    client.make_payment.return_value = {"status": "FAILED"}
    assert WalletGatewayAdapter(client).charge("01711111111", 100).message == "Payment failed"


def test_adapter_treats_unknown_status_as_failure():
    client = Mock()
    client.make_payment.return_value = {"status": "PENDING"}
    assert WalletGatewayAdapter(client).charge("01711111111", 100).success is False


def test_sandbox_client_completes_normal_payment():
    response = SandboxWalletClient().make_payment("01711111111", "500.00")
    assert response["status"] == "COMPLETED"
    assert response["trxID"].startswith("SBX")


def test_sandbox_client_rejects_zero_amount():
    response = SandboxWalletClient().make_payment("01711111111", "0.00")
    assert response == {"status": "FAILED", "error": "Invalid amount"}


def test_sandbox_client_fails_for_the_demo_failing_wallet():
    response = SandboxWalletClient().make_payment("01000000000", "500.00")
    assert response == {"status": "FAILED", "error": "Insufficient balance"}
