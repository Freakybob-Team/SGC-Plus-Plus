"""
SGC++

This module provides a simple interface for interacting with the SGC++ language. It includes methods for executing SGC++ code, handling variables, and removing comments.
"""

import re
from operations import gPrintln, gReadln
from utils import evaluate_expression
import importlib
class interpreter:
    def __init__(self):
        self.variables = {}

    def remove_comments(self, code):
        code = re.sub(r'//.*', '', code)
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        return code

    def execute(self, code):
        code = self.remove_comments(code)

        lines = code.split('\n')
        for line_num, line in enumerate(lines, start=1):
            line = line.strip()

            if not line:
                continue
            if line.startswith("import "):
                module_name = line.split(" ")[1]
                try:
                    self.variables[module_name] = importlib.import_module(module_name)
                    print(f"\033[32m[SUCCESS] Imported module '{module_name}'\033[0m")
                except Exception as e:
                    print(f"\033[31m[ERROR] Failed to import '{module_name}': {e}\033[0m")
                continue 
            
            var_match = re.match(r'var\s+(\w+)\s*=\s*(.*)', line)
            let_match = re.match(r'let\s+(\w+)\s*=\s*(.*)', line)
            if var_match:
                var_name, expr = var_match.groups()
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
                        result = evaluate_expression(expr, self.variables)
                        if result is not None:
                            self.variables[var_name] = result
                        else:
                            raise ValueError(f"\033[31m[ERROR] Invalid expression in assignment: {expr}\033[0m")
                except Exception as e:
                    print(f"\033[31m[ERROR] Error on line {line_num}: {e} \033[0m")
                    continue
            elif let_match:
                let_name, expr = let_match.groups()
                try:
                    if expr.startswith("["):
                        self.variables[let_name] = eval(expr)
                    elif expr.startswith("gPrintln"):
                        content = re.match(r'gPrintln\((.*?)\)', expr).group(1).strip()
                        self.variables[let_name] = gPrintln(content, self.variables)
                    elif expr.startswith("gReadln"):
                        prompt = re.match(r'gReadln\((.*?)\)', expr).group(1).strip()
                        self.variables[let_name] = gReadln(prompt, self.variables)
                    else:
                        result = evaluate_expression(expr, self.variables)
                        if result is not None:
                            self.variables[let_name] = result
                        else:
                            raise ValueError(f"\033[31m[ERROR] Invalid expression in assignment: {expr}\033[0m")
                except Exception as e:
                    print(f"\033[31m[ERROR] Error on line {line_num}: {e} \033[0m")
                    continue
            elif re.match(r'^\w+\.\w+\(.*\)$', line): 
                try:
                    evaluate_expression(line, self.variables)
                except Exception as e:
                    print(f"\033[31m[ERROR] Error on line {line_num}: {e} \033[0m")
                continue
            elif line.startswith("gPrintln"):
                content = re.match(r'gPrintln\((.*?)\)', line).group(1).strip()
                gPrintln(content, self.variables)

            elif line.startswith("gReadln"):
                prompt = re.match(r'gReadln\((.*?)\)', line).group(1).strip()
                gReadln(prompt, self.variables)

            else:
                print(f"\033[31m[ERROR] Syntax Error on line {line_num}: Unrecognized statement: {line} \033[0m")

    def run_file(self, filename):
        if filename.endswith(".sgc"):
            try:
                with open(filename, "r") as file:
                    code = file.read()
                    self.execute(code)
            except FileNotFoundError:
                print(f"\033[31m[ERROR] Error: File '{filename}' not found...\033[0m")
            except Exception as e:
                print(f"\033[31m[ERROR] Error reading file '{filename} :c': {e} \033[0m")
        else:
            print("\033[33m[WARNING] what.. this isn't sgc.. sob.. (Use a .sgc file plz :3)\033[0m")
