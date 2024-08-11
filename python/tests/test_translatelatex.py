import pytest
from src.translatelatex import translate

# Define test cases as a list of tuples (expression, expected_translation_result)
test_cases = [
    ("x=\\frac{1}{2}", "x=((1)/(2))"),
    ("y=xy^1+\\frac{1}{1^1}", "y=x*y^1+((1)/(1^1))"),
]
"""
Expression: \int _{-1}^11x^1\ dx
Translation Result: ∫((1*x^1),(x),(-1),(1))
"""
# Set the fixed parameters here
FIXED_PARAMS = {
    'TI_on': True,
    'SC_on': False,
    'constants_on': False,
    'coulomb_on': False,
    'e_on': False,
    'i_on': False,
    'g_on': False
}

@pytest.mark.parametrize(
    "expression, expected",
    test_cases
)
def test_translate(expression, expected):
    result = translate(
        expression,
        **FIXED_PARAMS  # Unpack fixed parameters here
    )
    assert result == expected, f"Expected '{expected}' but got '{result}'"
