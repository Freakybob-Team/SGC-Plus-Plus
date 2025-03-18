"""
SGC++

This module provides a simple interface for interacting with the SGC++ language. It includes methods for executing SGC++ code, handling variables, and removing comments.
"""
import sys
import re
from operations import gPrintln, gReadln
from utils import evaluate_expression
import importlib

class interpreter:
    def __init__(self):
        self.variables = {}
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
                    self.variables[module_name] = importlib.import_module(module_name)
                except Exception as e:
                    print(f"\033[31m[ERROR] Failed to import '{module_name}': {e}\033[0m")
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

            assign_match = re.match(r'(var|let)\s*(\w+)\s*=\s*(.*)', line)
            if assign_match:
                _, var_name, expr = assign_match.groups()
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
                        result = evaluate_expression(expr, {**self.variables, **self.builtins})
                        if result is not None:
                            self.variables[var_name] = result
                        else:
                            raise ValueError(f"\033[31m[ERROR] Invalid expression in assignment: {expr}\033[0m")
                except Exception as e:
                    print(f"\033[31m[ERROR] Error on line {i+1}: {e} \033[0m")
                i += 1
                continue

            elif re.match(r'\w+\s*=\s*.*', line):
                print(f"\033[31m[ERROR] Error on line {i+1}: Variables must be declared using 'let' or 'var'.\033[0m")
                i += 1
                continue

            elif re.match(r'^\w+\.\w+\(.*\)', line): 
                try:
                    evaluate_expression(line, self.variables)
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
