# Unit test __init__ ForecasterAutoregMultiVariate
# ==============================================================================
import re
import pytest
from pytest import approx
import numpy as np
import pandas as pd
from skforecast.ForecasterAutoregMultiVariate import ForecasterAutoregMultiVariate
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor


def test_init_exception_when_level_is_not_a_str():
    """
    Test exception is raised when level is not a str.
    """
    level = 5
    err_msg = re.escape(f"`level` argument must be a str. Got {type(level)}.")
    with pytest.raises(TypeError, match = err_msg):
        ForecasterAutoregMultiVariate(LinearRegression(), level=level, lags=2, steps=3)


def test_init_exception_when_steps_is_not_int():
    """
    Test exception is raised when steps is not an int.
    """
    steps = 'not_valid_type'
    err_msg = re.escape(
                f"`steps` argument must be an int greater than or equal to 1. "
                f"Got {type(steps)}."
            )
    with pytest.raises(TypeError, match = err_msg):
        ForecasterAutoregMultiVariate(LinearRegression(), level='l1', lags=2, steps=steps)


def test_init_exception_when_steps_is_less_than_1():
    """
    Test exception is raised when steps is less than 1.
    """
    steps = 0
    err_msg = re.escape(f"`steps` argument must be greater than or equal to 1. Got {steps}.")
    with pytest.raises(ValueError, match = err_msg):
        ForecasterAutoregMultiVariate(LinearRegression(), level='l1', lags=2, steps=steps)