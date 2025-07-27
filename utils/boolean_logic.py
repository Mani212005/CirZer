from sympy.logic import And, Or, Not, Xor
from sympy import symbols, sympify
from itertools import product

def parse_expression(expression_str):
    """
    Parses a boolean expression string into a sympy boolean expression.
    Supports &, |, ~, ^ for AND, OR, NOT, XOR.
    """
    # Define symbols for variables
    variables = sorted(list(set(filter(str.isalpha, expression_str))))
    
    # Create a dictionary to map variable names to sympy symbols
    symbol_map = {var: symbols(var) for var in variables}

    # Replace custom operators with sympy operators and variable names with symbols
    # This needs to be done carefully to avoid replacing parts of variable names
    # For simplicity, assuming single-letter variables for now.
    
    # First, replace operators
    parsed_str = expression_str.replace("&", " & ")
    parsed_str = parsed_str.replace("|", " | ")
    parsed_str = parsed_str.replace("~", " ~ ")
    parsed_str = parsed_str.replace("^", " ^ ")

    # Then, replace variable names with their symbolic representation
    # This step is crucial if variables are not single characters
    # For now, assuming single character variables as per typical boolean algebra
    
    # Use sympy's sympify to parse the expression
    # This handles operator precedence and parentheses correctly
    return sympify(parsed_str, evaluate=False)