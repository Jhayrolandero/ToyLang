#!/usr/bin/env python3
"""
Mini Chan Interpreter - Support for print statements, repeat loops, and variables
"""

import sys
import re

# Global variable dictionary
variables = {}

def run_chan_code(code):
    """
    Run Chan code that uses print statements, repeat loops, and variables.
    This is a very simple implementation that uses regex to parse the code.
    """
    # Remove comments
    code = re.sub(r'//.*', '', code)
    
    # Split into statements - anything between ; or }
    statements = []
    i = 0
    while i < len(code):
        # Skip whitespace
        while i < len(code) and code[i].isspace():
            i += 1
        
        if i >= len(code):
            break
            
        # Check for print statement: print("...")
        if code[i:i+5] == 'print':
            # Find the closing parenthesis
            start = code.find('(', i)
            if start == -1:
                raise Exception("Expected opening parenthesis after print")
                
            # Find matching closing parenthesis
            balance = 1
            end = start + 1
            while end < len(code) and balance > 0:
                if code[end] == '(':
                    balance += 1
                elif code[end] == ')':
                    balance -= 1
                end += 1
                
            if balance != 0:
                raise Exception("Unclosed parenthesis in print statement")
                
            statements.append(('print', code[start+1:end-1]))
            i = end
            
            # Skip semicolon if present
            while i < len(code) and code[i].isspace():
                i += 1
            if i < len(code) and code[i] == ';':
                i += 1
        
        # Check for let statement: let var = value
        elif code[i:i+3] == 'let':
            # Find the equals sign
            equals_pos = code.find('=', i + 3)
            if equals_pos == -1:
                raise Exception("Expected '=' in variable declaration")
                
            # Extract the variable name
            var_name = code[i+3:equals_pos].strip()
            
            # Find the end of the expression (semicolon)
            end = code.find(';', equals_pos)
            if end == -1:
                end = len(code)
                
            # Extract the value expression
            value_expr = code[equals_pos+1:end].strip()
            
            statements.append(('let', var_name, value_expr))
            i = end + 1
                
        # Check for repeat loop: repeat <count> times { ... }
        elif code[i:i+6] == 'repeat':
            # Find the 'times' keyword
            times_pos = code.find('times', i + 6)
            if times_pos == -1:
                raise Exception("Expected 'times' after repeat count")
                
            # Extract the count expression
            count_expr = code[i+6:times_pos].strip()
            
            # Find the opening brace
            brace_pos = code.find('{', times_pos)
            if brace_pos == -1:
                raise Exception("Expected opening brace after 'times'")
                
            # Find matching closing brace
            balance = 1
            end = brace_pos + 1
            while end < len(code) and balance > 0:
                if code[end] == '{':
                    balance += 1
                elif code[end] == '}':
                    balance -= 1
                end += 1
                
            if balance != 0:
                raise Exception("Unclosed braces in repeat loop")
                
            # Extract the loop body
            body = code[brace_pos+1:end-1]
            
            statements.append(('repeat', count_expr, body))
            i = end
        
        # Check for variable assignment: var = value
        elif '=' in code[i:] and code[i:code.find('=', i)].strip().isalnum():
            equals_pos = code.find('=', i)
            var_name = code[i:equals_pos].strip()
            
            # Find the end of the expression (semicolon)
            end = code.find(';', equals_pos)
            if end == -1:
                end = len(code)
                
            # Extract the value expression
            value_expr = code[equals_pos+1:end].strip()
            
            statements.append(('assign', var_name, value_expr))
            i = end + 1
            
        else:
            # Skip any other statement
            end = code.find(';', i)
            if end == -1:
                end = len(code)
            i = end + 1
    
    # Execute the statements
    execute_statements(statements)
    
def evaluate_expression(expr):
    """Evaluate a simple expression, handling variables and basic operations."""
    # Check if it's a quoted string
    if (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
        return expr[1:-1]
        
    # Check if it's just a variable reference
    if expr.strip().isalnum() and expr.strip() in variables:
        return variables[expr.strip()]
        
    # Check if it's a number
    try:
        return int(expr)
    except ValueError:
        pass
        
    # Check for addition
    if '+' in expr:
        parts = expr.split('+')
        if len(parts) == 2:
            left = evaluate_expression(parts[0].strip())
            right = evaluate_expression(parts[1].strip())
            
            # Handle string concatenation
            if isinstance(left, str) or isinstance(right, str):
                return str(left) + str(right)
            else:
                return left + right
                
    # If we can't parse it, return the expression itself
    return expr
    
def execute_statements(statements):
    """Execute a list of statements"""
    for stmt in statements:
        if stmt[0] == 'print':
            value = evaluate_expression(stmt[1])
            print(value)
            
        elif stmt[0] == 'let':
            var_name = stmt[1]
            value = evaluate_expression(stmt[2])
            variables[var_name] = value
            
        elif stmt[0] == 'assign':
            var_name = stmt[1]
            value = evaluate_expression(stmt[2])
            variables[var_name] = value
            
        elif stmt[0] == 'repeat':
            # Try to evaluate the count expression
            try:
                # First check if it's a simple variable reference
                if stmt[1] in variables:
                    count = variables[stmt[1]]
                else:
                    # Otherwise evaluate it as an expression
                    count = evaluate_expression(stmt[1])
                    
                # Make sure it's an integer
                count = int(count)
            except (ValueError, TypeError):
                # Default to 3 if we can't parse the count
                count = 3
                
            body = stmt[2]
            
            # Execute the loop body 'count' times
            for _ in range(count):
                # Parse and execute the body as a separate program
                run_chan_code(body)

def run_file(filename):
    """Run a Chan file"""
    global variables
    variables = {}  # Reset variables
    
    try:
        with open(filename, 'r') as file:
            code = file.read()
        run_chan_code(code)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
    except Exception as e:
        print(f"Error: {e}")

def main():
    if len(sys.argv) > 1:
        run_file(sys.argv[1])
    else:
        print("Usage: python mini_chan.py <filename>")

if __name__ == '__main__':
    main() 