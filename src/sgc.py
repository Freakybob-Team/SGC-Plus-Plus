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
        line_num = 0
        while line_num < len(lines):
            line = lines[line_num].strip()

            if not line:
                line_num += 1
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
                    print(f"Error on line {line_num + 1}: {e}")

            elif line.startswith("gPrintln"):
                content = re.match(r'gPrintln\((.*?)\)', line).group(1).strip()
                gPrintln(content, self.variables)

            elif line.startswith("gReadln"):
                prompt = re.match(r'gReadln\((.*?)\)', line).group(1).strip()
                gReadln(prompt, self.variables)

            elif line.startswith("for"):
                loop_match = re.match(r'for\s*\(var\s+(\w+)\s*=\s*(\d+);\s*\1\s*(<|<=|>|>=|==|!=)\s*(\d+);\s*\1\+\+\)', line)
                if loop_match:
                    var_name, start, condition, end = loop_match.groups()
                    start, end = int(start), int(end)

                    if var_name not in self.variables:
                        self.variables[var_name] = start

                    loop_body = []
                    line_num += 1
                    while line_num < len(lines) and not lines[line_num].strip().startswith("endfor"):
                        loop_body.append(lines[line_num].strip())
                        line_num += 1

                    if line_num >= len(lines) or not lines[line_num].strip().startswith("endfor"):
                        print(f"Syntax Error on line {line_num + 1}: Missing 'endfor'")
                    else:
                        while eval(f"{self.variables[var_name]} {condition} {end}"):
                            for loop_line in loop_body:
                                self.execute(loop_line)
                            self.variables[var_name] += 1
                else:
                    print(f"Syntax Error on line {line_num + 1}: Invalid for loop syntax (missing 'var'?)")
                    line_num += 1
                    continue

            else:
                print(f"Syntax Error on line {line_num + 1}: Unrecognized statement: {line}")

            line_num += 1

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
