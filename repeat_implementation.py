# Repeat Loop Implementation for Chan Language

# This file contains the implementation of the repeat loop feature
# Add this code to the Parser class

def repeat_loop(self):
    """repeat_loop : REPEAT expression TIMES LBRACE statement_list RBRACE"""
    self.eat('REPEAT')
    
    # Parse the expression for the number of times to repeat
    count_expr = self.expression()
    
    # Parse the "times" keyword
    self.eat('TIMES')
    
    # Parse the block of code to repeat
    self.eat('LBRACE')
    statements = self.statement_list()
    self.eat('RBRACE')
    
    return ('repeat', count_expr, statements)

# This code needs to be added to the Lexer's get_next_token method
# to recognize the 'times' keyword
"""
Add to the reserved words dictionary in the Parser class:
'times': 'TIMES',

Then in the Lexer's get_next_token method, add 'times' to the reserved words 
dictionary when handling identifiers.
"""

# Add this code to the Interpreter class to handle the repeat loop
"""
Add this to the evaluate method in the Interpreter class, inside the 
ntype handler:

elif ntype == 'repeat':
    # Evaluate the count expression
    count = self.evaluate(node[1], local_symbols)
    
    # Check if count is a number
    if not isinstance(count, int):
        raise Exception("Repeat count must be an integer")
    
    # Check if count is non-negative
    if count < 0:
        raise Exception("Repeat count cannot be negative")
    
    # Execute the statements multiple times
    result = None
    for _ in range(count):
        try:
            for stmt in node[2]:
                result = self.evaluate(stmt, local_symbols)
        except ReturnValue as rv:
            return rv.value
    
    return result
"""

# Usage:
"""
To use the repeat loop feature in Chan, you need to:
1. Add the repeat_loop method to the Parser class
2. Add 'times': 'TIMES' to the reserved words dictionary in the Parser
3. Add the repeat loop handling code to the Interpreter

Then you can use the repeat loop in your Chan programs like this:
repeat 3 times {
    print("Hello, world!");
}
""" 