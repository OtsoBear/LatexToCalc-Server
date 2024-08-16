import pytest
from src.translatelatex import translate

# Define test cases as a list of tuples (expression, expected_translation_result)
test_cases = [
    (r"x=\\frac{1}{2}", "x=((1)/(2))"),
    (r"y=xy^1+\\frac{1}{1^1}", "y=x*y^1+((1)/(1^1))"),
    (r"\sum_{i=1}^nx_i","∑(x,i,1,n)"),
    (r"\left(\begin{matrix} n\\ k \end{matrix}\right)=\dfrac{n!}{k!(n-k)!}", "nCr(n,k)=((n!)/(k!*(n-k)!))"),
    (r"\sqrt[n]{a}", "root(a,n)"),
    (r"{{a}^{\frac{1}{n}}}", "((a)^(((1)/(n))))"),
    (r"\log_{\mathrm{e}}x", "log(x,e)"),
    (r"\overline{AB}", "(AB)"),
    (r"\bar{a}\cdot \bar{b}", "dotP((a),(b))"),
    (r"\bar{a}\times \bar{b}", "crossP((a),(b))"),
    (r"\left(x_{n}\right)", "(x_(n))"),
    (r"\lim_{x \to a} f(x)", "lim_(xtoa)*f*(x)"),
    (r"\int_{ }^{ }f(x)\text{d}x", "int_()^()*f*(x)*dx"),
    (r"30°\cdot \frac{\pi }{180°}", "30°*((π)/(180°))")
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
        **FIXED_PARAMS  # Unpack fixed parameters her
    )
    assert result == expected, f"Expected '{expected}' but got '{result}'"
