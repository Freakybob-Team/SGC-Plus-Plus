"""
SGC++ Operations

This module provides functions for performing operations in SGC++. The functions include:
- gPrintln: Prints a message to the console, handling escape sequences like \n, \", etc., and also supporting f-strings.
- gReadln: Reads a line of input from the user and updates the associated variable with the input.
"""

from utils import evaluate_expression

def gPrintln(text, variables):
    try:
        result = None
        
        if isinstance(text, str) and text.startswith('f') and '{' in text and '}' in text:
            content = text[1:]
            if ((content.startswith('"') and content.endswith('"')) or 
                (content.startswith("'") and content.endswith("'"))):
                
                content = content[1:-1]
                
                idx = 0
                result = ""
                while idx < len(content):
                    if content[idx:idx+2] == '{{':  
                        result += '{'
                        idx += 2
                    elif content[idx:idx+2] == '}}':  
                        result += '}'
                        idx += 2
                    elif content[idx] == '{':
                        
                        end_idx = content.find('}', idx)
                        if end_idx == -1:
                            raise ValueError(f"Unclosed expression in f-string: {text}")
                        
                        
                        expr = content[idx+1:end_idx]
                        expr_value = evaluate_expression(expr.strip(), variables)
                        result += str(expr_value)
                        idx = end_idx + 1
                    else:
                        result += content[idx]
                        idx += 1
            else:
                raise ValueError(f"F-string must be quoted: {text}")
                
        
        elif text in variables:
            result = variables[text]
            
        
        elif (isinstance(text, str) and 
              ((text.startswith('"') and text.endswith('"')) or 
               (text.startswith("'") and text.endswith("'")))):
            result = text[1:-1]
            
        
        else:
            result = evaluate_expression(text, variables)

        
        if isinstance(result, str):
            
            escape_sequences = {
                '\\n': '\n', 
                '\\t': '\t', 
                '\\r': '\r', 
                '\\"': '"', 
                "\\'": "'",
                '\\\\': '\\',
                '\\p1': '(',
                '\\p2': ')',
            }
            
            for escape_seq, replacement in escape_sequences.items():
                result = result.replace(escape_seq, replacement)
        
        
        print(result)
        return result
        
    except Exception as e:
        print(f"\033[31m[ERROR] Print error: {str(e)}\033[0m")
        return None

def gReadln(prompt, variables):
    try:
        prompt_value = None

        if prompt in variables:
            prompt_value = str(variables[prompt])

        elif (isinstance(prompt, str) and 
              ((prompt.startswith('"') and prompt.endswith('"')) or 
               (prompt.startswith("'") and prompt.endswith("'")))):
            prompt_value = prompt[1:-1]
            
            
            escape_sequences = {
                '\\n': '\n', 
                '\\t': '\t', 
                '\\r': '\r', 
                '\\"': '"', 
                "\\'": "'",
                '\\\\': '\\',
                '\\p1': '(',
                '\\p2': ')',
            }
            
            for escape_seq, replacement in escape_sequences.items():
                prompt_value = prompt_value.replace(escape_seq, replacement)
                
        
        else:
            evaluated_prompt = evaluate_expression(prompt, variables)
            if evaluated_prompt is not None:
                prompt_value = str(evaluated_prompt)
            else:
                raise ValueError(f"Could not evaluate prompt: {prompt}")
        
        user_input = input(prompt_value)
        return user_input
        
    except KeyboardInterrupt:
        print("\n\033[31m[ERROR] Input was interrupted\033[0m")
        return None
    except Exception as e:
        print(f"\033[31m[ERROR] Input error: {str(e)}\033[0m")
        return None
