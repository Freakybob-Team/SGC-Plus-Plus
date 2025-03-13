"""
SGC++ Operations

This module provides functions for performing operations in SGC++. The functions include:
- `gPrintln`: Prints a message to the console, handling escape sequences like `\n`, `\"`, etc., and also supporting f-strings.
- `gReadln`: Reads a line of input from the user and updates the associated variable with the input.
"""

from utils import evaluate_expression

def gPrintln(text, variables):
    if text.startswith('f') and '{' in text and '}' in text:
        try:
            result = eval(text, {}, variables)
        except SyntaxError as e:
            print(f"Error processing f-string: {e}")
            return None
    else:
        result = variables.get(text, None) if text in variables else evaluate_expression(text, variables)

    if result is not None:
        print(result)
        return result
    else:
        print(f"Error: Could not evaluate '{text}'")
        return None


def gReadln(prompt, variables):
    prompt_value = "" if prompt in variables else prompt.strip('"').strip("'")
    user_input = input(f"{prompt_value} ")

    variables[prompt] = user_input
    return user_input
