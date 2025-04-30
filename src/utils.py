import re

def evaluate_expression(expr, variables):
    try:
        if '.' in expr and not expr.startswith('"') and not expr.startswith("'"):
            method_call_match = re.match(r'^([\w\.]+)\((.*)\)$', expr)
            if method_call_match:
                full_name = method_call_match.group(1)
                args_str = method_call_match.group(2)

                parts = full_name.split('.')

                if parts[0] in variables:
                    obj = variables[parts[0]]

                    if isinstance(obj, int):
                        raise TypeError(f"Attribute access not supported for 'int' type: '{expr}'")

                    for part in parts[1:-1]:
                        if hasattr(obj, part):
                            obj = getattr(obj, part)
                        else:
                            raise AttributeError(f"'{type(obj).__name__}' object has no attribute '{part}'")

                    method_name = parts[-1]
                    if hasattr(obj, method_name):
                        method = getattr(obj, method_name)

                        args = []
                        if args_str.strip():
                            current_arg = ""
                            in_string = False
                            string_char = None
                            paren_level = 0
                            bracket_level = 0

                            for char in args_str:
                                if char in ['"', "'"]:
                                    if not in_string:
                                        in_string = True
                                        string_char = char
                                    elif char == string_char:
                                        in_string = False

                                if not in_string:
                                    if char == '(':
                                        paren_level += 1
                                    elif char == ')':
                                        paren_level -= 1
                                    elif char == '[':
                                        bracket_level += 1
                                    elif char == ']':
                                        bracket_level -= 1

                                if char == ',' and not in_string and paren_level == 0 and bracket_level == 0:
                                    args.append(evaluate_expression(current_arg.strip(), variables))
                                    current_arg = ""
                                else:
                                    current_arg += char

                            if current_arg.strip():
                                args.append(evaluate_expression(current_arg.strip(), variables))

                        return method(*args)
                    else:
                        raise AttributeError(f"'{type(obj).__name__}' object has no attribute '{method_name}'")
                else:
                    raise NameError(f"name '{parts[0]}' is not defined")

            elif '.' in expr and '(' not in expr:
                parts = expr.split('.')
                if parts[0] in variables:
                    obj = variables[parts[0]]
                    for part in parts[1:]:
                        if hasattr(obj, part):
                            obj = getattr(obj, part)
                        else:
                            raise AttributeError(f"'{type(obj).__name__}' object has no attribute '{part}'")
                    return obj
                else:
                    raise NameError(f"name '{parts[0]}' is not defined")


        result = eval(expr, {"__builtins__": {}}, variables)
        return result
    except Exception as e:
        print(f"\033[31m[ERROR] Error evaluating expression '{expr}': {e}\033[0m")
        return None
