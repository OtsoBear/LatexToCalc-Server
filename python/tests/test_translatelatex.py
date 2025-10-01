"""
Test suite for LaTeX to Calculator translation
==============================================
This module tests the translatelatex.translate() function with various
LaTeX expressions and parameter combinations.
"""

import pytest
from src.translatelatex import translate


# ========================================================================
# TEST DATA STRUCTURES
# ========================================================================

class LaTeXTestCase:
    """Simple test case class for clarity"""
    def __init__(self, latex_input, expected_output, description="", params=None):
        self.latex_input = latex_input
        self.expected_output = expected_output
        self.description = description
        self.params = params or {}
    
    def __repr__(self):
        return f"LaTeXTestCase({self.description or self.latex_input[:20]}...)"


# ========================================================================
# BASIC FUNCTIONALITY TESTS (TI_on=True, all others False)
# ========================================================================

BASIC_TESTS = [
    # Fractions
    LaTeXTestCase(
        r"x=\\frac{1}{2}", 
        "x=((1)/(2))",
        "Simple fraction"
    ),
    LaTeXTestCase(
        r"y=xy^1+\\frac{1}{1^1}", 
        "y=x*y^1+((1)/(1^1))",
        "Mixed expression with fraction"
    ),
    
    # Subscripts
    LaTeXTestCase(
        r"m_1m_2", 
        "m₁*m₂",
        "Variable subscripts next to each other"
    ),
    LaTeXTestCase(
        r"T_\alpha + T_D = Q'",
        "T+T=Q'",  # Note: Greek letters become subscripts
        "Greek and regular subscripts"
    ),
    
    # Combinations
    LaTeXTestCase(
        r"\binom{n}{k}=\frac{n!}{k!(n-k)!}", 
        "nCr(n,k)=((n!)/(k!(n-k)!))",
        "Binomial coefficient"
    ),
    
    # Roots
    LaTeXTestCase(
        r"\sqrt[n]{a}", 
        "root(a,n)",
        "Nth root"
    ),
    LaTeXTestCase(
        r"{{a}^{\frac{1}{n}}}", 
        "((a)^(((1)/(n))))",
        "Power as root"
    ),
    
    # Logarithms
    LaTeXTestCase(
        r"\log_ex", 
        "log(x,e)",
        "Logarithm with base"
    ),
    
    # Vectors
    LaTeXTestCase(
        r"\overline{AB}", 
        "(AB)",
        "Vector notation"
    ),
    LaTeXTestCase(
        r"\bar{a}\cdot \bar{b}", 
        "dotP((a),(b))",
        "Dot product"
    ),
    LaTeXTestCase(
        r"\bar{a}\times \bar{b}", 
        "crossP((a),(b))",
        "Cross product"
    ),
    
    # Functions
    LaTeXTestCase(
        r"f_{Auto}",
        "f",  # Note: Auto becomes subscript characters
        "Function with subscript"
    ),
    LaTeXTestCase(
        r"t^{2\cdot 2}", 
        "t^(2*2)",
        "Exponent with operation"
    ),
    
    # Limits
    LaTeXTestCase(
        r"\lim _{x\rightarrow \infty ^-}\left(x+1\right)", 
        "lim(x+1,x,∞,-1)",
        "Limit to negative infinity"
    ),
    
    # Integrals
    LaTeXTestCase(
        r"\int _{ }^{ }f\left(x\right)dx", 
        "∫((f*(x)),(x))",
        "Indefinite integral"
    ),
    LaTeXTestCase(
        r"\int _{0}^{\infty }e^{-x}dx", 
        "∫((e^(-x)),(x),(0),(∞))",
        "Definite integral to infinity"
    ),
    # Units and angles
    LaTeXTestCase(
        r"30°\cdot \frac{\pi }{180°}", 
        "30°*((π)/(180°))",
        "Degree conversion"
    ),
    
    # Derivatives
    LaTeXTestCase(
        r"\frac{d}{dx}\left(\frac{x}{180\sin \left(\pi \right)}\right)",
        "(((x)/(180*sin(π))),x)",  # Note: TI Nspire uses special Unicode char for derivative
        "Derivative notation"
    ),
    LaTeXTestCase(
        r"\frac{d}{dt}\left(t^2\cdot\frac{d}{dx}\left(3x^2\right)\right)",
        "(t^2*(3*x^2,x),t)",  # Note: Nested derivatives with special char
        "Nested derivatives"
    ),
    LaTeXTestCase(
        r"D\left(3x^{22}\right)",
        "\uf008(3*x^(22),x)",  # Note: D notation includes special char
        "D notation for derivative"
    ),
]


# ========================================================================
# SCIENTIFIC CALCULATOR MODE TESTS (SC_on=True, TI_on=False)
# ========================================================================

SC_MODE_TESTS = [
    LaTeXTestCase(
        r"\binom{n}{k}",
        "nCr(n;k)",  # Note: SC mode uses semicolon
        "Binomial in SC mode"
    ),
    LaTeXTestCase(
        r"\pi",
        "(pi)",
        "Pi in SC mode"
    ),
    LaTeXTestCase(
        r"\log_{2}8",
        "log(2;8)",  # SC mode format
        "Log with base in SC mode"
    ),
]


# ========================================================================
# CONSTANTS MODE TESTS (constants_on=True)
# ========================================================================

CONSTANTS_TESTS = [
    LaTeXTestCase(
        r"F=ma",
        "F=m*a",  # Note: F becomes Faraday constant if its enabled
        "Force equation"
    ),
    LaTeXTestCase(
        r"E=mc^2",
        "E=m*_c^2",  # Note: c becomes speed of light constant
        "Energy equation"
    ),
    LaTeXTestCase(
        r"h\cdot v",
        "_h*v",  # Note: constants_on alone doesn't change h without \hbar
        "Planck constant"
    ),
    LaTeXTestCase(
        r"F=Q_evB",
        "F=(_q)*v*B",  # Note: Q_e becomes elementary charge constant
        "Magnetic force equation"
    ),
]


# ========================================================================
# SPECIAL SYMBOLS TESTS (e_on=True, i_on=True, g_on=True)
# ========================================================================

SPECIAL_SYMBOLS_TESTS = [
    # e_on=True tests
    LaTeXTestCase(
        r"e^x",
        "@e^x",
        "Euler's number",
        params={"e_on": True}
    ),
    
    # i_on=True tests
    LaTeXTestCase(
        r"z=x+iy",
        "z=x+@iy",
        "Complex number",
        params={"i_on": True}
    ),
    
    # g_on=True tests
    LaTeXTestCase(
        r"g=9.8",
        "_g=9.8",
        "Gravity constant",
        params={"g_on": True}
    ),
]


# ========================================================================
# UNITS MODE TESTS (units_on=True/False)
# ========================================================================

UNITS_TESTS = [
    LaTeXTestCase(
        r"\text{kg}",
        "(_kg)",
        "Kilogram unit",
        params={"units_on": True}
    ),
    LaTeXTestCase(
        r"10\text{m}",
        "10*(_m)",
        "Meter with value",
        params={"units_on": True}
    ),

]


# ========================================================================
# COMBINED PARAMETER TESTS
# ========================================================================

COMBINED_PARAMS_TESTS = [
    LaTeXTestCase(
        r"F=k\frac{q_1q_2}{r^2}",
        "F=_Cc*((q₁*q₂)/(r^2))",
        "Coulomb's law",
        params={"coulomb_on": True}
    ),
    LaTeXTestCase(
        r"E=\frac{1}{2}mv^2+mgh",
        "E=((1)/(2))*m*v^2+m*_g*h",
        "Energy equation with gravity",
        params={"g_on": True}
    ),
    LaTeXTestCase(
        r"e^{i\pi}+1=0",
        "@e^(@iπ)+1=0",
        "Euler's identity",
        params={"e_on": True, "i_on": True}
    ),
]


# ========================================================================
# PYTEST PARAMETRIZED TESTS
# ========================================================================

@pytest.mark.parametrize("test_case", BASIC_TESTS, ids=lambda tc: tc.description)
def test_basic_translation(test_case):
    """Test basic LaTeX translations with default TI mode settings"""
    result = translate(
        test_case.latex_input,
        TI_on=True,
        SC_on=False,
        constants_on=False,
        coulomb_on=False,
        e_on=False,
        i_on=False,
        g_on=False,
        units_on=True
    )
    assert result == test_case.expected_output, \
        f"Input: {test_case.latex_input}\nExpected: {test_case.expected_output}\nGot: {result}"


@pytest.mark.parametrize("test_case", SC_MODE_TESTS, ids=lambda tc: tc.description)
def test_sc_mode_translation(test_case):
    """Test Scientific Calculator mode translations"""
    result = translate(
        test_case.latex_input,
        TI_on=False,
        SC_on=True,
        constants_on=False,
        coulomb_on=False,
        e_on=False,
        i_on=False,
        g_on=False,
        units_on=True
    )
    assert result == test_case.expected_output, \
        f"Input: {test_case.latex_input}\nExpected: {test_case.expected_output}\nGot: {result}"


@pytest.mark.parametrize("test_case", CONSTANTS_TESTS, ids=lambda tc: tc.description)
def test_constants_mode(test_case):
    """Test constants mode translations"""
    result = translate(
        test_case.latex_input,
        TI_on=True,
        SC_on=False,
        constants_on=True,
        coulomb_on=False,
        e_on=False,
        i_on=False,
        g_on=False,
        units_on=True
    )
    assert result == test_case.expected_output, \
        f"Input: {test_case.latex_input}\nExpected: {test_case.expected_output}\nGot: {result}"


def test_special_symbols_with_custom_params():
    """Test special symbol replacements with custom parameters"""
    for test_case in SPECIAL_SYMBOLS_TESTS:
        params = {
            "TI_on": True,
            "SC_on": False,
            "constants_on": False,
            "coulomb_on": False,
            "e_on": False,
            "i_on": False,
            "g_on": False,
            "units_on": True
        }
        # Update with test-specific params
        if hasattr(test_case, 'params'):
            params.update(test_case.params)
        
        result = translate(test_case.latex_input, **params)
        assert result == test_case.expected_output, \
            f"Input: {test_case.latex_input}\nParams: {params}\nExpected: {test_case.expected_output}\nGot: {result}"


def test_units_mode():
    """Test units mode on/off behavior"""
    for test_case in UNITS_TESTS:
        params = {
            "TI_on": True,
            "SC_on": False,
            "constants_on": False,
            "coulomb_on": False,
            "e_on": False,
            "i_on": False,
            "g_on": False,
            "units_on": test_case.params.get("units_on", True)
        }
        
        result = translate(test_case.latex_input, **params)
        assert result == test_case.expected_output, \
            f"Input: {test_case.latex_input}\nParams: {params}\nExpected: {test_case.expected_output}\nGot: {result}"


def test_combined_parameters():
    """Test combinations of multiple parameters"""
    for test_case in COMBINED_PARAMS_TESTS:
        params = {
            "TI_on": True,
            "SC_on": False,
            "constants_on": False,
            "coulomb_on": False,
            "e_on": False,
            "i_on": False,
            "g_on": False,
            "units_on": True
        }
        # Update with test-specific params
        params.update(test_case.params)
        
        result = translate(test_case.latex_input, **params)
        assert result == test_case.expected_output, \
            f"Input: {test_case.latex_input}\nParams: {params}\nExpected: {test_case.expected_output}\nGot: {result}"


# ========================================================================
# CUSTOM PARAMETER COMBINATION TEST
# ========================================================================

def test_custom_parameter_combination():
    """
    Test any custom combination of parameters
    This is useful for testing specific scenarios
    """
    test_cases = [
        {
            "input": r"\frac{1}{2}kx^2",
            "params": {
                "TI_on": True,
                "SC_on": False,
                "constants_on": True,
                "coulomb_on": False,
                "e_on": False,
                "i_on": False,
                "g_on": False,
                "units_on": True
            },
            "expected": "((1)/(2))*_k*x^2",
            "description": "Spring energy with Boltzmann constant"
        },
        {
            "input": r"F=G\frac{m_1m_2}{r^2}",
            "params": {
                "TI_on": False,
                "SC_on": True,
                "constants_on": False,
                "coulomb_on": False,
                "e_on": False,
                "i_on": False,
                "g_on": False,
                "units_on": False
            },
            "expected": "F=G*((m₁*m₂)/(r^2))",
            "description": "Gravity formula in SC mode"
        }
    ]
    
    for test in test_cases:
        result = translate(test["input"], **test["params"])
        assert result == test["expected"], \
            f"Test: {test['description']}\nInput: {test['input']}\nParams: {test['params']}\nExpected: {test['expected']}\nGot: {result}"


# ========================================================================
# EDGE CASES AND REGRESSION TESTS
# ========================================================================

def test_edge_cases():
    """Test edge cases and potential problem areas"""
    edge_cases = [
        # Empty expressions
        LaTeXTestCase("", "", "Empty string"),
        
        # Single character
        LaTeXTestCase("x", "x", "Single variable"),
        
        # Complex nested structures
        LaTeXTestCase(
            r"\sqrt{\frac{1}{\sqrt{2}}}",
            "sqrt(((1)/(sqrt(2))))",
            "Nested sqrt and fraction"
        ),
        
        # Multiple operations
        LaTeXTestCase(
            r"a+b-c*d/e",
            "a+b-c*d/e",
            "Multiple operations"
        ),
    ]
    
    for test_case in edge_cases:
        result = translate(test_case.latex_input)
        assert result == test_case.expected_output, \
            f"Edge case '{test_case.description}' failed\nInput: {test_case.latex_input}\nExpected: {test_case.expected_output}\nGot: {result}"


# ========================================================================
# HELPER FUNCTION FOR MANUAL TESTING
# ========================================================================

def run_single_expression(latex_expr, **params):
    """
    Helper function for testing a single expression with custom parameters.
    Useful for debugging.
    
    Usage:
        result = test_single_expression(r"\\frac{1}{2}", TI_on=True)
    """
    default_params = {
        "TI_on": True,
        "SC_on": False,
        "constants_on": False,
        "coulomb_on": False,
        "e_on": False,
        "i_on": False,
        "g_on": False,
        "units_on": True
    }
    default_params.update(params)
    
    result = translate(latex_expr, **default_params)
    print(f"Input: {latex_expr}")
    print(f"Params: {params}")
    print(f"Result: {result}")
    return result


if __name__ == "__main__":
    # Run a quick test when executed directly
    print("Running quick test...")
    test_result = run_single_expression(r"\\frac{1}{2}mv^2", g_on=True)
    print(f"Quick test result: {test_result}")
