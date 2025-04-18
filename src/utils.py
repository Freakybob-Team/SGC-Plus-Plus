
"""
SGC++ Utils

This module provides utility functions for working with SGC++, including expression evaluation.

Functions:
- `evaluate_expression(expr, variables)`: Safely evaluates an expression string using the provided variables.


"""
def evaluate_expression(expr, variables):
    try:
        result = eval(expr, {"__builtins__": {}}, variables)
        return result
    except Exception as e:
        print(f"\033[31m[ERROR] Error evaluating expression '{expr}': {e}\033[0m")
        return None
