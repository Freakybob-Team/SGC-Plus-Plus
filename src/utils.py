
"""
SGC++ Utils

This module provides utility functions for working with SGC++, including expression evaluation.

Functions:
- `evaluate_expression(expr, variables)`: Safely evaluates an expression string using the provided variables.


"""
import importlib

def evaluate_expression(expr, variables):
    try:
        if expr.startswith('import '):
            module_name = expr.split(' ')[1]
            module = importlib.import_module(module_name)
            variables[module_name] = module
            return f"\033[32m[SUCCESS] Imported module '{module_name}'\033[0m"
        else:
            result = eval(expr, {"__builtins__": {}}, variables)
            
            if result is None and "(" in expr and ")" in expr:
                return "[INFO] Executed function successfully"
            return result
    except Exception as e:
        print(f"\033[31m[ERROR] Error evaluating expression '{expr}': {e}\033[0m")
        return None
