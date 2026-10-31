import pytest

from app.services.billing_strategies import (
    BillingStrategy,
    EqualSplitStrategy,
    PerMealRateStrategy,
)


def test_strategy_interface_cannot_be_instantiated():
    with pytest.raises(TypeError):
        BillingStrategy()


@pytest.mark.parametrize("strategy_class", [PerMealRateStrategy, EqualSplitStrategy])
def test_concrete_strategies_follow_the_interface(strategy_class):
    assert isinstance(strategy_class(), BillingStrategy)


def test_per_meal_rate_charges_by_meals():
    assert PerMealRateStrategy().calculate({1: 10, 2: 20}, 3000.0) == {1: 1000.0, 2: 2000.0}


def test_per_meal_rate_rounds_to_two_decimals():
    assert PerMealRateStrategy().calculate({1: 1, 2: 2}, 100.0) == {1: 33.33, 2: 66.67}


def test_per_meal_rate_member_without_meals_pays_nothing():
    assert PerMealRateStrategy().calculate({1: 0, 2: 10}, 500.0) == {1: 0.0, 2: 500.0}


def test_per_meal_rate_with_no_meals_at_all_charges_zero():
    assert PerMealRateStrategy().calculate({1: 0, 2: 0}, 500.0) == {1: 0.0, 2: 0.0}


def test_equal_split_ignores_meals():
    assert EqualSplitStrategy().calculate({1: 5, 2: 0, 3: 9}, 3000.0) == {1: 1000.0, 2: 1000.0, 3: 1000.0}


def test_equal_split_rounds_share_to_two_decimals():
    assert EqualSplitStrategy().calculate({1: 1, 2: 1, 3: 1}, 100.0) == {1: 33.33, 2: 33.33, 3: 33.33}


def test_equal_split_with_no_members_returns_empty():
    assert EqualSplitStrategy().calculate({}, 100.0) == {}
