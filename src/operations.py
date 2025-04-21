"""
SGC++ Operations

This module provides functions for performing operations in SGC++. The functions include:
- gPrintln: Prints a message to the console, handling escape sequences like \n, \", etc.., and also supporting f-strings and better support for stuff.
- gReadln: Reads a line of input from the user and attempts to convert it to the appropriate type.
"""

from utils import evaluate_expression

def gPrintln(text, variables, end="\n"):
    try:
        if isinstance(text, str) and ',' in text:
            parts = split_outside_quotes(text)
            results = []
            for part in parts:
                part = part.strip()
                result = process_print_item(part, variables)
                results.append(result)

            print(*results, sep=' ', end=end)
            return ' '.join(str(r) for r in results)

        elif isinstance(text, str) and '+' in text and not any(op in text for op in ['+=', '-=', '*=', '/=']):
            try:
                result = evaluate_expression(text, variables)
                print(result, end=end)
                return result
            except Exception:
                parts = text.split('+')
                result = ''
                for part in parts:
                    part = part.strip()
                    part_result = process_print_item(part, variables)
                    result += str(part_result)
                print(result, end=end)
                return result

        else:
            result = process_print_item(text, variables)
            print(result, end=end)
            return result

    except Exception as e:
        print(f"\033[31m[ERROR] Print error: {str(e)}\033[0m")
        return None

def split_outside_quotes(s):
    parts = []
    current = ''
    in_quotes = False
    quote_char = None
    
    i = 0
    while i < len(s):
        char = s[i]

        if char in ['"', "'"]:
            if not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char:
                if i > 0 and s[i-1] == '\\':
                    current += char
                else:
                    in_quotes = False
                    quote_char = None
            current += char
            
        elif char == ',' and not in_quotes:
            parts.append(current.strip())
            current = ''

        else:
            current += char
        
        i += 1
            
    if current:
        parts.append(current.strip())
    
    return parts

def process_print_item(text, variables):
    if isinstance(text, str) and text.startswith('f') and '{' in text and '}' in text:
        return process_fstring(text, variables)
    elif text in variables:
        return variables[text]
    elif (isinstance(text, str) and 
          ((text.startswith('"') and text.endswith('"')) or 
           (text.startswith("'") and text.endswith("'")))):
        result = text[1:-1]
        return process_escape_sequences(result)
    else:
        return evaluate_expression(text, variables)

def process_fstring(text, variables):
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
                    raise ValueError(f"\033[31m[ERROR] Unclosed expression in f-string: {text}\033[0m")
                
                expr = content[idx+1:end_idx]
                expr_value = evaluate_expression(expr.strip(), variables)
                result += str(expr_value)
                idx = end_idx + 1
            else:
                result += content[idx]
                idx += 1
        
        return process_escape_sequences(result)
    else:
        raise ValueError(f"\033[31m[ERROR] F-string must be quoted: {text}\033[0m")

def process_escape_sequences(text):
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
        text = text.replace(escape_seq, replacement)
    
    i = 0
    result = ""
    while i < len(text):
        if text[i:i+2] == '\\0' and i+4 < len(text) and text[i+2] == '3' and text[i+3] == '3':
            end_idx = text.find('m', i+4)
            if end_idx != -1:
                ansi_seq = '\033' + text[i+4:end_idx+1]
                result += ansi_seq
                i = end_idx + 1
                continue
        
        result += text[i]
        i += 1
    
    return result

def gReadln(prompt, variables):
    try:
        prompt_value = None

        if prompt in variables:
            prompt_value = str(variables[prompt])

        elif (isinstance(prompt, str) and 
              ((prompt.startswith('"') and prompt.endswith('"')) or 
               (prompt.startswith("'") and prompt.endswith("'")))):
            prompt_value = prompt[1:-1]
            prompt_value = process_escape_sequences(prompt_value)
                
        else:
            evaluated_prompt = evaluate_expression(prompt, variables)
            if evaluated_prompt is not None:
                prompt_value = str(evaluated_prompt)
            else:
                raise ValueError(f"\033[31m[ERROR] Could not evaluate prompt: {prompt}\033[0m")
        
        user_input = input(prompt_value)
        
        return convert_input_value(user_input)
        
    except KeyboardInterrupt:
        print("\n\033[31m[ERROR] Input was interrupted\033[0m")
        return None
    except Exception as e:
        print(f"\033[31m[ERROR] Input error: {str(e)}\033[0m")
        return None

def convert_input_value(input_str):
    try:
        if input_str.isdigit() or (input_str.startswith('-') and input_str[1:].isdigit()):
            return int(input_str)
    except ValueError:
        pass
    
    try:
        if '.' in input_str:
            return float(input_str)
    except ValueError:
        pass
    
    if input_str.lower() == 'true':
        return True
    elif input_str.lower() == 'false':
        return False
    
    return input_str
