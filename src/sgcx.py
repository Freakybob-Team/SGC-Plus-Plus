"""
SGC++

This module provides a simple interface for interacting with the SGC++ language. It includes methods for executing SGC++ code, if statements, while statements, for statements, handling variables, functions, function calls, and removing comments.
"""
import re
from operations import gPrintln, gReadln
from utils import evaluate_expression
import importlib
import os
import sys
import copy
import math

class interpreter:
    def __init__(self):
        self.variables = {}
        self.constants = set()
        self.functions = {}
        self.builtins = {
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'len': len,
            'abs': abs,
            'min': min,
            'max': max,
            'sum': sum,
            'round': round,
            'get': dict.get,
            'copy': copy.copy,
            'type': type,
            'list': list,
            'tuple': tuple,
            'set': set,
            'dict': dict,
            'print': print,
            'input': input,
            'range': range,
            'enumerate': enumerate,
            'zip': zip,
            'map': map,
            'filter': filter,
            'sorted': sorted,
            'chr': chr,
            'ord': ord,
            'bin': bin,
            'hex': hex,
            'oct': oct,
            'pow': pow,
            'divmod': divmod,
            'all': all,
            'any': any,
            'add': set.add
        }
        for name in dir(math):
            if not name.startswith("__"):
                self.builtins[name] = getattr(math, name)
                
        self.type_mappings = {
            'String': str,
            'Int': int,
            'Float': float,
            'Boolean': bool,
            'List': list,
            'Dict': dict,
            'Tuple': tuple,
            'Set': set,
        }

        self.modules = {}
        self.module_aliases = {}
        self.system_variables = {"__VERSION__": 1.7, "__AUTHOR__": "Freakybob-Team", "__LICENSE__": "MIT", "__name__": "__main__"}
        self.variables.update(self.builtins)
        for var in self.system_variables:
            self.variables[var] = self.system_variables[var]
            self.constants.add(var)


    def remove_comments(self, code):
        string_pattern = r'(\".*?\"|\'.*?\')'
        string_matches = list(re.finditer(string_pattern, code))
        string_placeholders = {}

        for i, match in enumerate(string_matches):
            placeholder = f"__STRING_PLACEHOLDER_{i}__"
            string_placeholders[placeholder] = match.group(0)
            code = code.replace(match.group(0), placeholder, 1)

        code = re.sub(r'//.*', '', code)
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)

        for placeholder, original in string_placeholders.items():
            code = code.replace(placeholder, original, 1)

        return code
        
    def _parse_import_statement(self, line):
        import_match = re.match(r'import\s+(\w+)(\s+as\s+(\w+))?', line)
        from_import_match = re.match(r'from\s+(\w+)\s+import\s+([*\w]+)(\s+as\s+(\w+))?', line)

        if import_match:
            module_name = import_match.group(1)
            alias = import_match.group(3) or module_name
            
            try:
                
                module = self._import_local_module(module_name)
                if module is None:  
                    module = importlib.import_module(module_name)
                
                self.modules[alias] = module
                self.module_aliases[alias] = module_name
                return True
            except Exception as e:
                print(f"\033[31m[ERROR] Failed to import '{module_name}': {e}\033[0m")
                return False

        elif from_import_match:
            module_name = from_import_match.group(1)
            import_items = from_import_match.group(2)
            alias = from_import_match.group(4)

            try:
                
                module = self._import_local_module(module_name)
                if module is None:  
                    module = importlib.import_module(module_name)
                
                if import_items == '*':
                    for name in dir(module):
                        if not name.startswith('_'):
                            if alias:
                                self.variables[f"{alias}.{name}"] = getattr(module, name)
                            else:
                                self.variables[name] = getattr(module, name)
                else:
                    items = [item.strip() for item in import_items.split(',')]
                    for item in items:
                        item_alias_match = re.match(r'(\w+)\s+as\s+(\w+)', item)
                        if item_alias_match:
                            original_name = item_alias_match.group(1)
                            local_alias = item_alias_match.group(2)
                            
                            if hasattr(module, original_name):
                                if alias:
                                    self.variables[f"{alias}.{local_alias}"] = getattr(module, original_name)
                                else:
                                    self.variables[local_alias] = getattr(module, original_name)
                        else:
                            if hasattr(module, item):
                                if alias:
                                    self.variables[f"{alias}.{item}"] = getattr(module, item)
                                else:
                                    self.variables[item] = getattr(module, item)
                
                if alias:
                    self.modules[alias] = module
                    self.module_aliases[alias] = module_name

                return True
            except Exception as e:
                print(f"\033[31m[ERROR] Failed to import from '{module_name}': {e}\033[0m")
                return False

        return False
    
    def _import_local_module(self, module_name):       
        possible_paths = [
            f"{module_name}.py",
            f"./{module_name}.py",
            f"{module_name}/__init__.py"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    abs_path = os.path.abspath(path)
                    module_name_to_use = module_name
                    spec = importlib.util.spec_from_file_location(module_name_to_use, abs_path)
                    if spec is None:
                        continue
            
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name_to_use] = module
                    spec.loader.exec_module(module)
                    return module
                except Exception as e:
                    print(f"\033[31m[ERROR] Failed to import local file '{path}': {e}\033[0m")
        
        return None

    
    
    def _get_indentation_level(self, line):
        return len(line) - len(line.lstrip())
    
    def _get_indented_block(self, lines, start_index, base_indent):
        block = []
        i = start_index
        
        
        while i < len(lines) and not lines[i].strip():
            i += 1
            
        if i >= len(lines):
            return block, i
        
        
        expected_indent = self._get_indentation_level(lines[i])
        
        if expected_indent <= base_indent:
            print(f"\033[31m[ERROR] Indentation error on line {i+1}: Expected increased indentation level\033[0m")
            return block, i
        
        while i < len(lines):
            line = lines[i]
            
            
            if not line.strip():
                block.append(line)
                i += 1
                continue
                
            indent = self._get_indentation_level(line)
            
            
            if indent <= base_indent:
                break
                
            
            
            if indent >= expected_indent:
                block.append(line)
                i += 1
            else:
                
                print(f"\033[31m[ERROR] Inconsistent indentation on line {i+1}: Expected at least {expected_indent} spaces but got {indent}\033[0m")
                i += 1
            
        return block, i
    
    def _type_check(self, value, expected_type_name):
        expected_type = self.type_mappings.get(expected_type_name)
        if expected_type is None:
            print(f"\033[31m[ERROR] Unknown type: {expected_type_name}\033[0m")
            return False
            
        if value is None:
            return expected_type_name == "None"
            
        return isinstance(value, expected_type)

    def _call_function(self, func_name, args):
        if func_name not in self.functions:
            print(f"\033[31m[ERROR] Function '{func_name}' is not defined\033[0m")
            return None
            
        func_info = self.functions[func_name]
        func_body = func_info['body']
        param_names = func_info['params']
        param_defaults = func_info.get('defaults', {})
        
        if len(args) < len(param_names):
            missing_params = param_names[len(args):]
            for param in missing_params:
                if param not in param_defaults:
                    print(f"\033[31m[ERROR] Function '{func_name}' expects {len(param_names)} arguments, but got {len(args)}\033[0m")
                    return None
        elif len(args) > len(param_names):
            print(f"\033[31m[ERROR] Function '{func_name}' expects {len(param_names)} arguments, but got {len(args)}\033[0m")
            return None
    
        old_vars = self.variables.copy()
        
        for i, param in enumerate(param_names[:len(args)]):
            self.variables[param] = args[i]
            
        for i in range(len(args), len(param_names)):
            param = param_names[i]
            if param in param_defaults:
                default_info = param_defaults[param]
                decl_type = default_info['decl_type']
                expr = default_info['expr']
                
                try:
                    result = evaluate_expression(expr, {**self.variables, **self.builtins, **self.modules})
                    self.variables[param] = result
                    if decl_type == 'const':
                        self.constants.add(param)
                except Exception as e:
                    print(f"\033[31m[ERROR] Error evaluating default value for parameter '{param}': {e}\033[0m")
                    self.variables = old_vars
                    return None
    
        result = None
        try:
            self.execute("\n".join(func_body))
            
            if 'return_value' in self.variables:
                result = self.variables['return_value']
                del self.variables['return_value']
        except Exception as e:
            print(f"\033[31m[ERROR] Error in function '{func_name}': {e}\033[0m")
            
        self.variables = old_vars
        
        return result

    
    def _process_f_string(self, f_string):
        if f_string.startswith('f"') or f_string.startswith("f'"):
        
            if f_string.startswith('f"'):
                content = f_string[2:-1]  
            else:
                content = f_string[2:-1]  
        
        
            for var_match in re.finditer(r'\{([^{}]+)\}', content):
                var_expr = var_match.group(1)
                try:
                    value = evaluate_expression(var_expr, self.variables)
                    content = content.replace(f"{{{var_expr}}}", str(value))
                except Exception as e:
                    print(f"\033[31m[ERROR] Error evaluating variable '{var_expr}' in f-string: {e}\033[0m")
        
            return content
        return f_string
    
    
    def _parse_function_args(self, args_str):
        if not args_str.strip():
            return []
        args = []
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
                args.append(current_arg.strip())
                current_arg = ""
            else:
                current_arg += char
                
        if current_arg.strip():
            args.append(current_arg.strip())
            
        return args
    
    def execute(self, code):
        code = self.remove_comments(code)
        lines = code.split('\n')
        i = 0

        while i < len(lines):
            line = lines[i].strip()
            curr_indent = self._get_indentation_level(lines[i])
            if not line:
                i += 1
                continue

            if line.startswith("import ") or line.startswith("from "):
                if self._parse_import_statement(line):
                    i += 1
                    continue
                
            
            while_match = re.match(r'while\s+(.*?):', line)
            if while_match:
                condition = while_match.group(1)
                loop_body, next_idx = self._get_indented_block(lines, i+1, curr_indent)
                
                if not loop_body:
                    print(f"\033[31m[ERROR] Empty while loop body on line {i+1}\033[0m")
                    i = next_idx
                    continue
                    
                while bool(evaluate_expression(condition, self.variables)):
                    self.variables.pop('continue', None)  
                    self.execute("\n".join(loop_body))
                    
                    if 'break' in self.variables:
                        del self.variables['break']
                        break
                    
                    if 'continue' in self.variables:
                        del self.variables['continue']
                        
                i = next_idx
                continue


            for_match = re.match(r'for\s+(.*?):', line)
            if for_match:
                for_expr = for_match.group(1).strip()
                loop_body, next_idx = self._get_indented_block(lines, i+1, curr_indent)
                
                classic_match = re.match(r'\((.*?);(.*?);(.*?)\)', for_expr)
                if classic_match:
                    init, condition, update = classic_match.groups()
                    self.execute(init.strip())
                    
                    while bool(evaluate_expression(condition.strip(), self.variables)):
                        self.variables.pop('continue', None)  
                        self.execute("\n".join(loop_body))
                        
                        if 'break' in self.variables:
                            del self.variables['break']
                            break
                            
                        if 'continue' in self.variables:
                            del self.variables['continue']
                            
                            
                        self.execute(update.strip())
                
                in_match = re.match(r'(\w+)\s+in\s+(.*)', for_expr)
                if in_match:
                    var_name, collection_expr = in_match.groups()
                    try:
                        collection = evaluate_expression(collection_expr, self.variables)
                        
                        if isinstance(collection, (list, tuple, str, dict, set)):
                            for item in collection:
                                self.variables.pop('continue', None)  
                                self.variables[var_name] = item
                                self.execute("\n".join(loop_body))
                                
                                if 'break' in self.variables:
                                    del self.variables['break']
                                    break
                                    
                                if 'continue' in self.variables:
                                    del self.variables['continue']
                                    continue  
                        else:
                            print(f"\033[31m[ERROR] Cannot iterate over {type(collection).__name__}\033[0m")
                    except Exception as e:
                        print(f"\033[31m[ERROR] Error in for-in loop: {e}\033[0m")
                
                range_match = re.match(r'(\w+)\s+in\s+range\((.*?)\)', for_expr)
                if range_match:
                    var_name, range_args = range_match.groups()
                    try:
                        args = [arg.strip() for arg in range_args.split(',')]
                        range_values = []
                        
                        if len(args) == 1:
                            end = int(evaluate_expression(args[0], self.variables))
                            range_values = range(end)
                        elif len(args) == 2:
                            start = int(evaluate_expression(args[0], self.variables))
                            end = int(evaluate_expression(args[1], self.variables))
                            range_values = range(start, end)
                        elif len(args) == 3:
                            start = int(evaluate_expression(args[0], self.variables))
                            end = int(evaluate_expression(args[1], self.variables))
                            step = int(evaluate_expression(args[2], self.variables))
                            range_values = range(start, end, step)
                        
                        for val in range_values:
                            self.variables.pop('continue', None)  
                            self.variables[var_name] = val
                            self.execute("\n".join(loop_body))
                            
                            if 'break' in self.variables:
                                del self.variables['break']
                                break
                                
                            if 'continue' in self.variables:
                                del self.variables['continue']
                                continue  
                    except Exception as e:
                        print(f"\033[31m[ERROR] Error in range-based loop: {e}\033[0m")
                
                i = next_idx
                continue
            
            if line.strip() == "break":
                self.variables['break'] = True
                i += 1
                continue
                
            if line.strip() == "continue":
                self.variables['continue'] = True
                i += 1
                continue


            if line.startswith("exit("):
                match = re.match(r'exit\((\d+)\)', line.strip())
                if match:
                    exit_code = int(match.group(1))
                else:
                    exit_code = 0
                self.variables['exit_code'] = exit_code
                color = "\033[32m" if exit_code == 0 else "\033[31m"
                reset = "\033[0m"
                print("-" * 50)
                input(f"Exited with code: {color}{exit_code}{reset}. Press enter to exit...")
                sys.exit(exit_code)
                


            if_match = re.match(r'if\s+(.*?):', line)
            if if_match:
                condition = if_match.group(1)
                try:
                    if "isinstance" in condition:
                        match = re.match(r'isinstance\((.*?),\s*(\w+)\)', condition)
                        if match:
                            var_name = match.group(1).strip()
                            type_name = match.group(2).strip()
                            if var_name in self.variables:
                                type_obj = eval(type_name, self.builtins)
                                condition_result = isinstance(self.variables[var_name], type_obj)
                            else:
                                print(f"\033[31m[ERROR] Variable '{var_name}' does not exist.\033[0m")
                                condition_result = False
                        else:
                            condition_result = bool(evaluate_expression(condition, self.variables))
                    else:
                        condition_result = bool(evaluate_expression(condition, self.variables))

                    if_block, next_idx = self._get_indented_block(lines, i+1, curr_indent)
                
                    block_executed = False
                    new_i = next_idx
                
                    if condition_result:
                        self.execute("\n".join(if_block))
                        block_executed = True
                
                    while new_i < len(lines):
                        next_line = lines[new_i].strip()
                        elif_match = re.match(r'elif\s+(.*?):', next_line)
                        if not elif_match:
                            break
                        
                        if not block_executed:
                            elif_condition = elif_match.group(1)
                            elif_condition_result = bool(evaluate_expression(elif_condition, self.variables))
                        
                            elif_block, next_idx = self._get_indented_block(lines, new_i+1, curr_indent)
                            new_i = next_idx
                        
                            if elif_condition_result:
                                self.execute("\n".join(elif_block))
                                block_executed = True
                        else:
                            _, next_idx = self._get_indented_block(lines, new_i+1, curr_indent)
                            new_i = next_idx
                
                    if new_i < len(lines) and lines[new_i].strip() == "else:":
                        if not block_executed:
                            else_block, next_idx = self._get_indented_block(lines, new_i+1, curr_indent)
                            self.execute("\n".join(else_block))
                        else:
                            _, next_idx = self._get_indented_block(lines, new_i+1, curr_indent)
                        new_i = next_idx
                    
                    i = new_i
                    continue
                except Exception as e:
                    print(f"\033[31m[ERROR] Error evaluating if condition on line {i+1}: {e}\033[0m")
                    i += 1
                    continue
        
            if line.startswith("elif") or line == "else:":
                print(f"\033[31m[ERROR] '{line}' without preceding 'if' statement on line {i+1}\033[0m")
                i += 1
                continue

            compound_assign_match = re.match(r'(\w+)\s*(\+=|\-=|\*=|\/=|%=|\*\*=|\/\/=|&=|\|=|\^=|<<=|>>=)\s*(.*)', line)
            if compound_assign_match:
                var_name, operator, expr = compound_assign_match.groups()
                if var_name in self.system_variables:
                    print(f"\033[31m[ERROR] '{var_name}' is a variable that cannot be changed due to being a system variable.\033[0m")
                    i += 1
                    continue
                if var_name in self.constants:
                    print(f"\033[31m[ERROR] Cannot modify constant '{var_name}'.\033[0m")
                    i += 1
                    continue
                if var_name not in self.variables:
                    print(f"\033[31m[ERROR] Variable '{var_name}' does not exist. Declare it first.\033[0m")
                    i += 1
                    continue
                
                try:
                    current_value = self.variables[var_name]
                    result = evaluate_expression(expr, {**self.variables, **self.builtins, **self.modules})
                
                    if operator == '+=':
                        self.variables[var_name] = current_value + result
                    elif operator == '-=':
                        self.variables[var_name] = current_value - result
                    elif operator == '*=':
                        self.variables[var_name] = current_value * result
                    elif operator == '/=':
                        self.variables[var_name] = current_value / result
                    elif operator == '%=':
                        self.variables[var_name] = current_value % result
                    elif operator == '**=':
                        self.variables[var_name] = current_value ** result
                    elif operator == '//=':
                        self.variables[var_name] = current_value // result
                    elif operator == '&=':
                        self.variables[var_name] = current_value & result
                    elif operator == '|=':
                        self.variables[var_name] = current_value | result
                    elif operator == '^=':
                        self.variables[var_name] = current_value ^ result
                    elif operator == '<<=':
                        self.variables[var_name] = current_value << result
                    elif operator == '>>=':
                        self.variables[var_name] = current_value >> result
                except Exception as e:
                    print(f"\033[31m[ERROR] Error on line {i+1}: {e}\033[0m")
                i += 1
                continue


            typed_variable = re.match(r'(var|let|const)\s*(\w+):\s*(\w+)\s*=\s*(.*)', line)
            if typed_variable:
                decl_type, var_name, type_name, expr = typed_variable.groups()
                if var_name in self.system_variables:
                    print(f"\033[31m[ERROR] '{var_name}' is a variable that cannot be changed due to being a system variable.\033[0m")
                    i += 1
                    continue
                if var_name in self.variables and decl_type == 'const':
                    print(f"\033[31m[ERROR] Cannot redefine constant: {var_name}\033[0m")
                    i += 1
                    continue
                
                try:
                    expr = expr.strip()
                    if expr.lower() == 'null':
                        result = None
                    elif expr.startswith("["):
                        result = eval(expr)
                    elif expr.startswith("gPrintln"):
                        content = re.match(r'gPrintln\((.*?)\)', expr).group(1).strip()
                        result = gPrintln(content, self.variables)
                    elif expr.startswith("gReadln"):
                        prompt = re.match(r'gReadln\((.*?)\)', expr).group(1).strip()
                        result = gReadln(prompt, self.variables)
                    else:
                        result = evaluate_expression(expr, {**self.variables, **self.builtins, **self.modules})
                    
                    if not self._type_check(result, type_name):
                        print(f"\033[31m[ERROR] Type error on line {i+1}: Expected {type_name} but got {type(result).__name__} for variable '{var_name}'\033[0m")
                        i += 1
                        continue
                        
                    self.variables[var_name] = result
                    if decl_type == 'const':
                        self.constants.add(var_name)
                except Exception as e:
                    print(f"\033[31m[ERROR] Error on line {i+1}: {e}\033[0m")
                i += 1
                continue
            
            const_match = re.match(r'const\s*(\w+)\s*=\s*(.*)', line)
            if const_match:
                var_name, expr = const_match.groups()
                if var_name in self.system_variables:
                    print(f"\033[31m[ERROR] '{var_name}' is a variable that cannot be changed due to being a system variable.\033[0m")
                elif var_name in self.variables:
                    print(f"\033[31m[ERROR] Cannot redefine existing variable or constant: {var_name}\033[0m")
                else:
                    try:
                        result = evaluate_expression(expr, {**self.variables, **self.builtins, **self.modules})
                        self.variables[var_name] = result
                        self.constants.add(var_name)
                    except Exception as e:
                        print(f"\033[31m[ERROR] Error on line {i+1}: {e}\033[0m")
                i += 1
                continue
            
            
            assign_match = re.match(r'(var|let)\s*(\w+)\[(\d+)\]\s*=\s*(.*)', line)
            if assign_match:
                _, var_name, index, expr = assign_match.groups()
                if var_name in self.system_variables:
                    print(f"\033[31m[ERROR] '{var_name}' is a variable that cannot be changed due to being a system variable.\033[0m")
                    i += 1
                    continue
                try:
                    index = int(index)
                    if var_name in self.constants:
                        print(f"\033[31m[ERROR] Cannot reassign constant '{var_name}'.\033[0m")
                    elif var_name in self.variables and isinstance(self.variables[var_name], list):
                        list_var = self.variables[var_name]
                        if index < len(list_var):
                            result = evaluate_expression(expr, {**self.variables, **self.builtins, **self.modules})
                            if result is not None:
                                list_var[index] = result
                            else:
                                print(f"\033[31m[ERROR] Invalid expression in assignment: {expr}\033[0m")
                        else:
                            print(f"\033[31m[ERROR] Index {index} out of range for list '{var_name}'\033[0m")
                    else:
                        print(f"\033[31m[ERROR] '{var_name}' is not a list or doesn't exist.\033[0m")
                except Exception as e:
                    print(f"\033[31m[ERROR] Error on line {i+1}: {e}\033[0m")
                i += 1
                continue
            
            assign_match = re.match(r'(var|let|const)\s*(\w+)\s*=\s*(.*)', line)
            if assign_match:
                _, var_name, expr = assign_match.groups()
                if var_name in self.system_variables:
                    print(f"\033[31m[ERROR] '{var_name}' is a variable that cannot be changed due to being a system variable.\033[0m")
                    i += 1
                    continue
                if var_name in self.variables and _ == 'const':
                    print(f"\033[31m[ERROR] Cannot redefine constant: {var_name}\033[0m")
                else:
                    try:
                        expr = expr.strip()
                        if expr.lower() == 'null':
                            result = None
                        elif expr.startswith("["):
                            result = eval(expr)
                        elif expr.startswith("gPrintln"):
                            content = re.match(r'gPrintln\((.*?)\)', expr).group(1).strip()
                            result = gPrintln(content, self.variables)
                        elif expr.startswith("gReadln"):
                            prompt = re.match(r'gReadln\((.*?)\)', expr).group(1).strip()
                            result = gReadln(prompt, self.variables)
                        elif re.match(r'(\w+)\((.*?)\)', expr) and re.match(r'(\w+)\((.*?)\)', expr).group(1) in self.functions:
                            func_match = re.match(r'(\w+)\((.*?)\)', expr)
                            func_name = func_match.group(1)
                            args_str = func_match.group(2).strip()

                            args = []
                            if args_str:
                                arg_parts = self._parse_function_args(args_str)
                                for arg in arg_parts:
                                    try:
                                        value = evaluate_expression(arg, self.variables)
                                        args.append(value)
                                    except Exception as e:
                                        print(f"\033[31m[ERROR] Error evaluating argument '{arg}': {e}\033[0m")
                                        break

                            result = self._call_function(func_name, args)
                        else:
                            result = evaluate_expression(expr, {**self.variables, **self.builtins, **self.modules})
                        self.variables[var_name] = result
                        if _ == 'const':
                            self.constants.add(var_name)
                    except Exception as e:
                        print(f"\033[31m[ERROR] Error on line {i+1}: {e}\033[0m")
                i += 1
                continue
            
            reassign_match = re.match(r'(\w+)\s*=\s*(.*)', line)
            if reassign_match:
                var_name, expr = reassign_match.groups()
                if var_name in self.system_variables:
                    print(f"\033[31m[ERROR] '{var_name}' is a variable that cannot be changed due to being a system variable.\033[0m")
                if var_name in self.constants:
                    print(f"\033[31m[ERROR] Cannot reassign constant '{var_name}'.\033[0m")
                elif var_name not in self.variables:
                    print(f"\033[31m[ERROR] Variable '{var_name}' does not exist. Declare it first.\033[0m")
                else:
                    try:
                        expr = expr.strip()
                        if expr.lower() == 'null':
                            result = None
                        elif expr.startswith("["):
                            result = eval(expr)
                        elif expr.startswith("gPrintln"):
                            content = re.match(r'gPrintln\((.*?)\)', expr).group(1).strip()
                            result = gPrintln(content, self.variables)
                        elif expr.startswith("gReadln"):
                            prompt = re.match(r'gReadln\((.*?)\)', expr).group(1).strip()
                            result = gReadln(prompt, self.variables)
                        elif re.match(r'(\w+)\((.*?)\)', expr) and re.match(r'(\w+)\((.*?)\)', expr).group(1) in self.functions:
                            func_match = re.match(r'(\w+)\((.*?)\)', expr)
                            func_name = func_match.group(1)
                            args_str = func_match.group(2).strip()

                            args = []
                            if args_str:
                                arg_parts = self._parse_function_args(args_str)
                                for arg in arg_parts:
                                    try:
                                        value = evaluate_expression(arg, self.variables)
                                        args.append(value)
                                    except Exception as e:
                                        print(f"\033[31m[ERROR] Error evaluating argument '{arg}': {e}\033[0m")
                                        break

                            result = self._call_function(func_name, args)
                        else:
                            result = evaluate_expression(expr, {**self.variables, **self.builtins, **self.modules})
                        self.variables[var_name] = result
                    except Exception as e:
                        print(f"\033[31m[ERROR] Error on line {i+1}: {e}\033[0m")
                i += 1
                continue


            multi_var_assign_match = re.match(r'(var|let|const)\s+([\w\s,]+)\s*=\s*(.*)', line)
            if multi_var_assign_match:
                decl_type, var_names_str, values_str = multi_var_assign_match.groups()
                var_names = [name.strip() for name in var_names_str.split(',')]
                
                if ',' in values_str:
                    values = []
                    current_value = ""
                    in_string = False
                    string_char = None
                    paren_level = 0
                    bracket_level = 0
                    
                    for char in values_str:
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
                            values.append(current_value.strip())
                            current_value = ""
                        else:
                            current_value += char
                            
                    if current_value.strip():
                        values.append(current_value.strip())
                    
                    if len(var_names) != len(values):
                        print(f"\033[31m[ERROR] Number of variables ({len(var_names)}) doesn't match number of values ({len(values)})\033[0m")
                    else:
                        for var_idx, (var_name, value_expr) in enumerate(zip(var_names, values)):
                            if var_name in self.system_variables:
                                print(f"\033[31m[ERROR] '{var_name}' is a variable that cannot be changed due to being a system variable.\033[0m")
                                continue
                            if var_name in self.variables and decl_type == 'const':
                                print(f"\033[31m[ERROR] Cannot redefine constant: {var_name}\033[0m")
                                continue
                                
                            try:
                                value_expr = value_expr.strip()
                                if value_expr.lower() == 'null':
                                    value = None
                                elif value_expr.startswith("["):
                                    value = eval(value_expr)
                                elif value_expr.startswith("gPrintln"):
                                    content_match = re.match(r'gPrintln\((.*?)\)', value_expr)
                                    if content_match:
                                        content = content_match.group(1).strip()
                                        value = gPrintln(content, self.variables)
                                    else:
                                        print(f"\033[31m[ERROR] Invalid gPrintln format: {value_expr}\033[0m")
                                        continue
                                elif value_expr.startswith("gReadln"):
                                    prompt_match = re.match(r'gReadln\((.*?)\)', value_expr)
                                    if prompt_match:
                                        prompt = prompt_match.group(1).strip()
                                        value = gReadln(prompt, self.variables)
                                    else:
                                        print(f"\033[31m[ERROR] Invalid gReadln format: {value_expr}\033[0m")
                                        continue
                                elif re.match(r'(\w+)\((.*?)\)', value_expr) and re.match(r'(\w+)\((.*?)\)', value_expr).group(1) in self.functions:
                                    func_match = re.match(r'(\w+)\((.*?)\)', value_expr)
                                    func_name = func_match.group(1)
                                    args_str = func_match.group(2).strip()
            
                                    args = []
                                    if args_str:
                                        arg_parts = self._parse_function_args(args_str)
                                        for arg in arg_parts:
                                            try:
                                                arg_value = evaluate_expression(arg, self.variables)
                                                args.append(arg_value)
                                            except Exception as e:
                                                print(f"\033[31m[ERROR] Error evaluating argument '{arg}': {e}\033[0m")
                                                break
            
                                    value = self._call_function(func_name, args)
                                else:
                                    value = evaluate_expression(value_expr, {**self.variables, **self.builtins, **self.modules})
                                    
                                self.variables[var_name] = value
                                if decl_type == 'const':
                                    self.constants.add(var_name)
                            except Exception as e:
                                print(f"\033[31m[ERROR] Error evaluating value for '{var_name}': {e}\033[0m")
                else:
                    try:
                        value_expr = values_str.strip()
                        if value_expr.lower() == 'null':
                            result = None
                        elif value_expr.startswith("["):
                            result = eval(value_expr)
                        elif value_expr.startswith("gPrintln"):
                            content = re.match(r'gPrintln\((.*?)\)', value_expr).group(1).strip()
                            result = gPrintln(content, self.variables)
                        elif value_expr.startswith("gReadln"):
                            prompt = re.match(r'gReadln\((.*?)\)', value_expr).group(1).strip()
                            result = gReadln(prompt, self.variables)
                        elif re.match(r'(\w+)\((.*?)\)', value_expr) and re.match(r'(\w+)\((.*?)\)', value_expr).group(1) in self.functions:
                            func_match = re.match(r'(\w+)\((.*?)\)', value_expr)
                            func_name = func_match.group(1)
                            args_str = func_match.group(2).strip()
            
                            args = []
                            if args_str:
                                arg_parts = self._parse_function_args(args_str)
                                for arg in arg_parts:
                                    try:
                                        arg_value = evaluate_expression(arg, self.variables)
                                        args.append(arg_value)
                                    except Exception as e:
                                        print(f"\033[31m[ERROR] Error evaluating argument '{arg}': {e}\033[0m")
                                        break
            
                            result = self._call_function(func_name, args)
                        else:
                            result = evaluate_expression(value_expr, {**self.variables, **self.builtins, **self.modules})
                        
                        for var_name in var_names:
                            if var_name in self.system_variables:
                                print(f"\033[31m[ERROR] '{var_name}' is a variable that cannot be changed due to being a system variable.\033[0m")
                                continue
                            if var_name in self.variables and decl_type == 'const':
                                print(f"\033[31m[ERROR] Cannot redefine constant: {var_name}\033[0m")
                                continue
                                
                            self.variables[var_name] = result
                            if decl_type == 'const':
                                self.constants.add(var_name)
                    except Exception as e:
                        print(f"\033[31m[ERROR] Error on line {i+1}: {e}\033[0m")
                
                i += 1
                continue
            
        
                    
            
            func_match = re.match(r'func\s+(\w+)\((.*?)\):', line)
            if func_match:
                func_name = func_match.group(1)
                params_str = func_match.group(2).strip()
                params = []
                param_defaults = {}
                
                if params_str:
                    param_parts = []
                    current_part = ""
                    in_string = False
                    string_char = None
                    paren_level = 0
                    bracket_level = 0
                    
                    for char in params_str:
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
                            param_parts.append(current_part.strip())
                            current_part = ""
                        else:
                            current_part += char
                            
                    if current_part.strip():
                        param_parts.append(current_part.strip())
                    
                    for param in param_parts:
                        param = param.strip()
                        if not param:
                            continue
                            
                        if "=" in param:
                            var_match = re.match(r'(var|let|const)?\s*(\w+)\s*=\s*(.*)', param)
                            if var_match:
                                decl_type, param_name, default_expr = var_match.groups()
                                params.append(param_name)
                                param_defaults[param_name] = {
                                    'expr': default_expr,
                                    'decl_type': decl_type or 'var'
                                }
                            else:
                                parts = param.split('=', 1)
                                param_name = parts[0].strip()
                                default_expr = parts[1].strip()
                                params.append(param_name)
                                param_defaults[param_name] = {
                                    'expr': default_expr,
                                    'decl_type': 'var'
                                }
                        elif ":" in param:
                            type_match = re.match(r'(var|let|const)?\s*(\w+)\s*:\s*(\w+)', param)
                            if type_match:
                                decl_type, param_name, _ = type_match.groups()
                                params.append(param_name)
                            else:
                                params.append(param)
                        else:
                            var_match = re.match(r'(var|let|const)?\s*(\w+)', param)
                            if var_match:
                                _, param_name = var_match.groups()
                                params.append(param_name)
                            else:
                                params.append(param)
                
                func_body, next_idx = self._get_indented_block(lines, i+1, curr_indent)
                
                if not func_body:
                    print(f"\033[31m[ERROR] Empty function body for '{func_name}' on line {i+1}\033[0m")
                    i += 1
                    continue
                    
                self.functions[func_name] = {
                    'params': params,
                    'defaults': param_defaults,
                    'body': func_body
                }
                
                i = next_idx
                continue

                
            func_call_match = re.match(r'(\w+)\((.*?)\)', line)
            if func_call_match and func_call_match.group(1) in self.functions:
                func_name = func_call_match.group(1)
                args_str = func_call_match.group(2).strip()
                
                args = []
                if args_str:
                    arg_parts = self._parse_function_args(args_str)
                    for arg in arg_parts:
                        try:
                            value = evaluate_expression(arg, self.variables)
                            args.append(value)
                        except Exception as e:
                            print(f"\033[31m[ERROR] Error evaluating argument '{arg}': {e}\033[0m")
                            break
                
                self._call_function(func_name, args)
                i += 1
                continue
                
            
            
            if line.startswith("return"):
                return_expr = line[6:].strip()  
                try:
                    if return_expr:  
                        if return_expr.startswith('f"') or return_expr.startswith("f'"):
                            return_value = self._process_f_string(return_expr)
                        elif return_expr.startswith("gPrintln"):
                            content = re.match(r'gPrintln\((.*?)\)', return_expr).group(1).strip()
                            return_value = gPrintln(content, self.variables)
                        elif return_expr.startswith("gReadln"):
                            prompt = re.match(r'gReadln\((.*?)\)', return_expr).group(1).strip()
                            return_value = gReadln(prompt, self.variables)
                        else:
                            return_value = evaluate_expression(return_expr, self.variables)
                        self.variables['return_value'] = return_value
                    else:  
                        self.variables['return_value'] = None
                except Exception as e:
                    print(f"\033[31m[ERROR] Error in return statement: {e}\033[0m")
                break  




            elif re.match(r'\w+\s*=\s*.*', line):
                print(f"\033[31m[ERROR] Error on line {i+1}: Variables must be declared using 'let', 'var' or 'const'.\033[0m")
                i += 1
                continue

            elif re.match(r'^\w+\.\w+\(.*\)', line): 
                try:
                    evaluate_expression(line, {**self.variables, **self.modules})
                except Exception as e:
                    print(f"\033[31m[ERROR] Error on line {i+1}: {e} \033[0m")
                i += 1
                continue
            
            elif line.startswith("gPrintln"):
                content = re.match(r'gPrintln\((.*?)\)', line).group(1).strip()
                gPrintln(content, self.variables)
                i += 1
                continue

            elif line.startswith("gReadln"):
                prompt = re.match(r'gReadln\((.*?)\)', line).group(1).strip()
                gReadln(prompt, self.variables)
                i += 1
                continue

            else:
                print(f"\033[31m[ERROR] Syntax Error on line {i+1}: Unrecognized statement: {line} \033[0m")
                i += 1
                continue
                

    def run_file(self, filename):
        if filename.endswith(".sgcx"):
            try:
                with open(filename, "r") as file:
                    code = file.read()
                    self.execute(code)
                    if not code.strip():
                        print("\033[33m[WARNING] File is empty.. add some code!\033[0m")
            except FileNotFoundError:
                print(f"\033[31m[ERROR] Error: File '{filename}' not found...\033[0m")
            except Exception as e:
                print(f"\033[31m[ERROR] Error reading file '{filename} :c': {e} \033[0m")
        else:
            print("\033[33m[WARNING] what.. this isn't sgc++.. sob.. (Use a .sgcx file plz :3)\033[0m")
