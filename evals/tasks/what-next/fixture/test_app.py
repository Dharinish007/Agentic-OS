from app import to_fahrenheit


def test_freezing():
    assert to_fahrenheit(0) == 32


def test_boiling():
    assert to_fahrenheit(100) == 212
