"""
SGC++

This module provides a simple interface for interacting with the SGC++ language. It includes methods for executing SGC++ code, if statements, while statements, for statements, handling variables, and removing comments.
"""
import sys
import re
from operations import gPrintln, gReadln
from utils import evaluate_expression
import importlib

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
            'round': round
        }
        self.modules = {}

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

    def execute(self, code):
        code = self.remove_comments(code)
        lines = code.split('\n')
        i = 0

        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue

            if line.startswith("import "):
                module_name = line.split(" ")[1]
                try:
                    self.modules[module_name] = importlib.import_module(module_name)
                except Exception as e:
                    print(f"\033[31m[ERROR] Failed to import '{module_name}': {e}\033[0m")
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
                    sys.exit(exit_code)
                else:
                    sys.exit(0)

            if_match = re.match(r'if \((.*?)\) then', line)
            if if_match:
                condition = if_match.group(1)
                try:
                    condition_result = bool(evaluate_expression(condition, self.variables))
                    inside_if_block = []
                    i += 1

                    while i < len(lines) and not re.match(r'^(else|end)$', lines[i].strip()):
                        inside_if_block.append(lines[i])
                        i += 1

                    else_block = []
                    if i < len(lines) and lines[i].strip() == "else":
                        i += 1
                        while i < len(lines) and lines[i].strip() != "end":
                            else_block.append(lines[i])
                            i += 1
                    
                    if i < len(lines) and lines[i].strip() == "end":
                        i += 1
                    
                    if condition_result:
                        self.execute("\n".join(inside_if_block))
                    elif else_block:
                        self.execute("\n".join(else_block))
                    continue
                except Exception as e:
                    print(f"\033[31m[ERROR] Error evaluating if condition: {e}\033[0m")
                    return
            
            
            const_match = re.match(r'const\s*(\w+)\s*=\s*(.*)', line)
            if const_match:
                var_name, expr = const_match.groups()
                if var_name in self.variables:
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

            assign_match = re.match(r'(var|let)\s*(\w+)\s*=\s*(.*)', line)
            if assign_match:
                _, var_name, expr = assign_match.groups()
                if var_name in self.variables:
                    print(f"\033[31m[ERROR] Variable '{var_name}' already exists. Use simple assignment without 'var', 'let' or 'const'.\033[0m")
                else:
                    try:
                        if expr.startswith("["):
                            self.variables[var_name] = eval(expr)
                        elif expr.startswith("gPrintln"):
                            content = re.match(r'gPrintln\((.*?)\)', expr).group(1).strip()
                            self.variables[var_name] = gPrintln(content, self.variables)
                        elif expr.startswith("gReadln"):
                            prompt = re.match(r'gReadln\((.*?)\)', expr).group(1).strip()
                            self.variables[var_name] = gReadln(prompt, self.variables)
                        else:
                            result = evaluate_expression(expr, {**self.variables, **self.builtins, **self.modules})
                            if result is not None:
                                self.variables[var_name] = result
                            else:
                                raise ValueError(f"\033[31m[ERROR] Invalid expression in assignment: {expr}\033[0m")
                    except Exception as e:
                        print(f"\033[31m[ERROR] Error on line {i+1}: {e}\033[0m")
                i += 1
                continue

            reassign_match = re.match(r'(\w+)\s*=\s*(.*)', line)
            if reassign_match:
                var_name, expr = reassign_match.groups()
                if var_name in self.constants:
                    print(f"\033[31m[ERROR] Cannot reassign constant '{var_name}'.\033[0m")
                elif var_name not in self.variables:
                    print(f"\033[31m[ERROR] Variable '{var_name}' does not exist. Declare it first.\033[0m")
                else:
                    try:
                        result = evaluate_expression(expr, {**self.variables, **self.builtins, **self.modules})
                        if result is not None:
                            self.variables[var_name] = result
                        else:
                            print(f"\033[31m[ERROR] Invalid expression in assignment: {expr}\033[0m")
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
