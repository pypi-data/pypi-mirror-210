"""Test samplers module."""

from dataclasses import dataclass
from slot_machine import SlotsSerializer


@dataclass(slots=True)
class Basket(SlotsSerializer):
    """Define basket class."""

    chicken_nuggets: int
    price: float


def test_sample_basket():
    basket_distribution = """
chicken_nuggets: !SampleRange 10..20
price: !SampleUniform 9.99..20.0
"""
    basket = Basket.from_yaml(basket_distribution)
    assert isinstance(basket.chicken_nuggets, int)
    assert isinstance(basket.price, float)
    assert 10 <= basket.chicken_nuggets <= 20
    assert 9.99 <= basket.price <= 20.0


def test_scalar_samplers():
    """Test scalar samplers."""
    yaml_str = """
    a: !SampleUniform 1..2
    b: !SampleRange 1..2
    """

    @dataclass(slots=True)
    class Params(SlotsSerializer):
        a: float
        b: int

    params = Params.from_yaml(yaml_str)

    assert isinstance(params.a, float)
    assert 1 <= params.a <= 2

    assert isinstance(params.b, int)
    assert params.b == 1


def test_sequence_samplers():
    """Test sequence samplers."""
    yaml_str = """
    a: !Choose ["x", "y", "y"]
    b: !ChooseInteger [1, 2, 2]
    c: !ChooseFloat [.1, .2, .2]
    """

    @dataclass(slots=True)
    class Params(SlotsSerializer):
        a: str
        b: int
        c: float

    params = Params.from_yaml(yaml_str)

    assert isinstance(params.a, str)
    assert params.a in ["x", "y"]

    assert isinstance(params.b, int)
    assert params.b in [1, 2]

    assert isinstance(params.c, float)
    assert 0.1 <= params.c <= 0.2


def test_mapping_samplers():
    """Test mapping samplers."""
    yaml_str = """
    a: !SampleNormal
        mu: 0.0
        sigma: 1.0
    """

    @dataclass(slots=True)
    class Params(SlotsSerializer):
        a: float

    params = Params.from_yaml(yaml_str)

    assert isinstance(params.a, float)
