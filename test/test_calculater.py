from main import add, subtract, multiply, divide
import pytest

def test_add():
    assert add(1,2) == 3

def test_subtract():
    assert subtract(5,3) == 2

def test_multiply():
    assert multiply(4,3) == 12

def test_divide():
    assert divide(8,2) == 4

def test_divide_zero():
    import pytest
    with pytest.raises(ValueError):
        divide(4,0)