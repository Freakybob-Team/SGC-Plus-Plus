"""
SGC++

This module provides a simple interface for interacting with the SGC++ language. It includes methods for executing SGC++ code, if statements, while statements, for statements, handling variables, and removing comments.
"""
import re
from operations import gPrintln, gReadln
from utils import evaluate_expression
import importlib
import sys

class interpreter:
    def __init__(self):
        self.variables = {}
        self.constants = set()
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
        }
        self.modules = {}
        self.module_aliases = {}
        self.system_variables = {"__VERSION__": 1.5, "__AUTHOR__": "Freakybob-Team", "__LICENSE__": "MIT"}
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
    
    
    def _get_indentation_level(self, line):
        return len(line) - len(line.lstrip())
    
    def _get_indented_block(self, lines, start_index, base_indent):
        block = []
        i = start_index
        
        if i >= len(lines) or self._get_indentation_level(lines[i]) <= base_indent:
            return block, i
            
        expected_indent = self._get_indentation_level(lines[i])
        
        if expected_indent <= base_indent:
            print(f"\033[31m[ERROR] Indentation error on line {i+1}: Expected increased indentation level\033[0m")
            return block, i
        
        while i < len(lines):
            line = lines[i]
            if not line.strip():
                i += 1
                continue
                
            indent = self._get_indentation_level(line)
            
            if indent > base_indent and indent != expected_indent:
                print(f"\033[31m[ERROR] Inconsistent indentation on line {i+1}\033[0m")
            
            if indent <= base_indent: 
                break
                
            block.append(line)
            i += 1
            
        return block, i
    
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
                
            
            while_match = re.match(r'while \((.*?)\) do', line)
            if while_match:
                condition = while_match.group(1)
                loop_body = []
                i += 1

                while i < len(lines) and lines[i].strip() != "end":
                    loop_body.append(lines[i])
                    i += 1

                if i < len(lines) and lines[i].strip() == "end":
                    i += 1

                while bool(evaluate_expression(condition, self.variables)):
                    self.execute("\n".join(loop_body))
                    if 'break' in self.variables:
                        del self.variables['break']
                        break
                continue

            for_match = re.match(r'for \((.*?)\) do', line)
            if for_match:
                loop_parts = for_match.group(1).split(";")
                if len(loop_parts) != 3:
                    print(f"\033[31m[ERROR] Invalid for loop syntax on line {i+1}\033[0m")
                    return

                init, condition, update = loop_parts
                self.execute(init.strip())

                loop_body = []
                i += 1

                while i < len(lines) and lines[i].strip() != "end":
                    loop_body.append(lines[i])
                    i += 1

                if i < len(lines) and lines[i].strip() == "end":
                    i += 1

                while bool(evaluate_expression(condition.strip(), self.variables)):
                    self.execute("\n".join(loop_body))
                    self.execute(update.strip())
                    if 'break' in self.variables:
                        del self.variables['break']
                        break
                continue

            if line.strip() == "break":
                self.variables['break'] = True
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
                


            if_match = re.match(r'if\s+\((.*?)\):', line)
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
                        elif_match = re.match(r'elif\s+\((.*?)\):', next_line)
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
                        else:
                            result = evaluate_expression(expr, {**self.variables, **self.builtins, **self.modules})
                        self.variables[var_name] = result
                    except Exception as e:
                        print(f"\033[31m[ERROR] Error on line {i+1}: {e}\033[0m")
                i += 1
                continue


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
