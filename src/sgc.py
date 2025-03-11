"""
SGC++

This module provides a simple interface for interacting with the SGC++ language. It includes methods for executing SGC++ code, handling variables, and removing comments.
"""

import re
from operations import gPrintln, gReadln
from utils import evaluate_expression

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

            var_match = re.match(r'var\s+(\w+)\s*=\s*(.*)', line)
            if var_match:
                var_name, expr = var_match.groups()
                try:
                    if expr.startswith("gPrintln"):
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
                            raise ValueError(f"Invalid expression in assignment: {expr}")
                except Exception as e:
                    print(f"Error on line {line_num}: {e}")
                    continue

            elif line.startswith("gPrintln"):
                content = re.match(r'gPrintln\((.*?)\)', line).group(1).strip()
                gPrintln(content, self.variables)

            elif line.startswith("gReadln"):
                prompt = re.match(r'gReadln\((.*?)\)', line).group(1).strip()
                gReadln(prompt, self.variables)

            else:
                print(f"Syntax Error on line {line_num}: Unrecognized statement: {line}")

    def run_file(self, filename):
        if filename.endswith(".sgc"):
            try:
                with open(filename, "r") as file:
                    code = file.read()
                    self.execute(code)
            except FileNotFoundError:
                print(f"Error: File '{filename}' not found...")
            except Exception as e:
                print(f"Error reading file '{filename} :c': {e}")
        else:
            print("what.. this isn't sgc.. sob.. (Use a .sgc file plz :3)")
