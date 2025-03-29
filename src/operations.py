"""
SGC++ Operations

This module provides functions for performing operations in SGC++. The functions include:
- gPrintln: Prints a message to the console, handling escape sequences like \n, \", etc., and also supporting f-strings.
- gReadln: Reads a line of input from the user and updates the associated variable with the input.
"""

from utils import evaluate_expression

def gPrintln(text, variables):
    if text.startswith('f') and '{' in text and '}' in text:
        try:
            result = eval(text, {}, variables)
        except SyntaxError as e:
            print(f"\033[31m[ERROR] Error processing f-string: {e}\033[0m")
            return None
    else:
        result = variables.get(text, None) if text in variables else evaluate_expression(text, variables)

    if result is not None:
        print(result)
        return result
    else:
        print(f"\033[31m[ERROR] Error: Could not evaluate '{text}' \033[0m")
        return None


"""
SGC++ Operations

This module provides functions for performing operations in SGC++. The functions include:
- gPrintln: Prints a message to the console, handling escape sequences like \n, \", etc., and also supporting f-strings.
- gReadln: Reads a line of input from the user and updates the associated variable with the input.
"""

from utils import evaluate_expression

def gPrintln(text, variables):
    if text.startswith('f') and '{' in text and '}' in text:
        try:
            result = eval(text, {}, variables)
        except SyntaxError as e:
            print(f"\033[31m[ERROR] Error processing f-string: {e}\033[0m")
            return None
    else:
        result = variables.get(text, None) if text in variables else evaluate_expression(text, variables)

    if result is not None:
        print(result)
        return result
    else:
        print(f"\033[31m[ERROR] Error: Could not evaluate '{text}' \033[0m")
        return None


def gReadln(prompt, variables=None):
    if prompt not in variables:
        prompt_value = prompt.strip('"').strip("'")
    else:
        prompt_value = variables[prompt]

    try:
        user_input = input(f"{prompt_value} ")
        return user_input
    except Exception as e:
        print(f"\033[31m[ERROR] Error: {e}\033[0m")
        return None
    except KeyboardInterrupt:
        print("\033[31m[ERROR] Error: input was interrupted\033[0m")
        return None
