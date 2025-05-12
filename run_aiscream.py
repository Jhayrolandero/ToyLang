#!/usr/bin/env python3

import sys
from use_case import Lexer, Parser, Interpreter, Token, ReturnValue

def patch_interpreter():
    """Patch the interpreter to support the repeat loop feature."""
    
    # Add 'times' to the reserved words in Lexer
    def patched_get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
                
            # Handle single-line comments
            if self.current_char == '/' and self.peek() == '/':
                self.skip_comment()
                continue
                
            if self.current_char in ('\"', "'"):
                return Token('STRING', self.get_string(), self.lineno)
                
            if self.current_char.isdigit():
                return Token('NUMBER', self.get_number(), self.lineno)
                
            if self.current_char.isalpha() or self.current_char == '_':
                identifier = self.get_identifier()
                # Check if it's a reserved word or boolean literal
                reserved = {
                    'def': 'DEF',
                    'return': 'RETURN',
                    'if': 'IF',
                    'else': 'ELSE',
                    'while': 'WHILE',
                    'for': 'FOR',
                    'print': 'PRINT',
                    'input': 'INPUT',
                    'parseInt': 'PARSEINT',
                    'parallel': 'PARALLEL',
                    'repeat': 'REPEAT',
                    'times': 'TIMES',  # Added times keyword
                    'and': 'AND',
                    'or': 'OR',
                    'not': 'NOT',
                    'struct': 'STRUCT',
                    'true': 'BOOLEAN',
                    'false': 'BOOLEAN',
                    'class': 'CLASS',
                    'new': 'NEW',
                    'let': 'LET',
                    'const': 'CONST'
                }
                if identifier in reserved:
                    if identifier in ('true', 'false'):
                        return Token(reserved[identifier], identifier == 'true', self.lineno)
                    return Token(reserved[identifier], identifier, self.lineno)
                return Token('ID', identifier, self.lineno)
                
            # Handle multi-character operators first
            if self.current_char == '=' and self.peek() == '=':
                self.advance()
                self.advance()
                return Token('EQ', '==', self.lineno)
                
            if self.current_char == '!' and self.peek() == '=':
                self.advance()
                self.advance()
                return Token('NE', '!=', self.lineno)
                
            if self.current_char == '>' and self.peek() == '=':
                self.advance()
                self.advance()
                return Token('GE', '>=', self.lineno)
                
            if self.current_char == '<' and self.peek() == '=':
                self.advance()
                self.advance()
                return Token('LE', '<=', self.lineno)
                
            # Handle arrow function
            if self.current_char == '-' and self.peek() == '>':
                self.advance()
                self.advance()
                return Token('ARROW', '=>', self.lineno)
                
            # Also handle alternative arrow syntax (=>)
            if self.current_char == '=' and self.peek() == '>':
                self.advance()
                self.advance()
                return Token('ARROW', '=>', self.lineno)
                
            # Single-character tokens
            if self.current_char == '+':
                self.advance()
                return Token('PLUS', '+', self.lineno)
                
            if self.current_char == '-':
                self.advance()
                return Token('MINUS', '-', self.lineno)
                
            if self.current_char == '*':
                self.advance()
                return Token('TIMES', '*', self.lineno)
                
            if self.current_char == '/':
                self.advance()
                return Token('DIVIDE', '/', self.lineno)
                
            if self.current_char == '=':
                self.advance()
                return Token('EQUALS', '=', self.lineno)
                
            if self.current_char == '(':
                self.advance()
                return Token('LPAREN', '(', self.lineno)
                
            if self.current_char == ')':
                self.advance()
                return Token('RPAREN', ')', self.lineno)
                
            if self.current_char == '{':
                self.advance()
                return Token('LBRACE', '{', self.lineno)
                
            if self.current_char == '}':
                self.advance()
                return Token('RBRACE', '}', self.lineno)
                
            if self.current_char == '[':
                self.advance()
                return Token('LBRACKET', '[', self.lineno)
                
            if self.current_char == ']':
                self.advance()
                return Token('RBRACKET', ']', self.lineno)
                
            if self.current_char == ',':
                self.advance()
                return Token('COMMA', ',', self.lineno)
                
            if self.current_char == ';':
                self.advance()
                return Token('SEMICOLON', ';', self.lineno)
                
            if self.current_char == ':':
                self.advance()
                return Token('COLON', ':', self.lineno)
                
            if self.current_char == '.':
                self.advance()
                return Token('DOT', '.', self.lineno)
                
            if self.current_char == '>':
                self.advance()
                return Token('GT', '>', self.lineno)
                
            if self.current_char == '<':
                self.advance()
                return Token('LT', '<', self.lineno)
                
            self.error(f"Invalid character '{self.current_char}'")
            
        return Token('EOF', None, self.lineno)
    
    # Replace the get_next_token method
    Lexer.get_next_token = patched_get_next_token
    
    # Add the repeat_loop method to the Parser class
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
    
    Parser.repeat_loop = repeat_loop
    
    # Modify the compound_statement method
    old_compound_statement = Parser.compound_statement
    
    def new_compound_statement(self):
        token = self.current_token
        if token.type == 'REPEAT':
            return self.repeat_loop()
        return old_compound_statement(self)
    
    Parser.compound_statement = new_compound_statement
    
    # Add the repeat handler to the Interpreter
    old_evaluate = Interpreter.evaluate
    
    def new_evaluate(self, node, local_symbols=None):
        if local_symbols is None:
            local_symbols = {}
            
        if isinstance(node, tuple):
            ntype = node[0]
            
            if ntype == 'repeat':
                # Evaluate the count expression
                count = old_evaluate(self, node[1], local_symbols)
                
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
                            result = old_evaluate(self, stmt, local_symbols)
                    except ReturnValue as rv:
                        return rv.value
                
                return result
            
        return old_evaluate(self, node, local_symbols)
    
    Interpreter.evaluate = new_evaluate

def run_chan_file(filename, debug=False):
    """Run a Chan file with repeat loop support."""
    try:
        # Apply the patches
        patch_interpreter()
        
        # Open and read the file
        with open(filename, 'r') as file:
            source_code = file.read()
        
        # Run the code
        lexer = Lexer(source_code)
        parser = Parser(lexer)
        interpreter = Interpreter(parser, debug=debug)
        interpreter.interpret()
        
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        run_chan_file(sys.argv[1], debug='--debug' in sys.argv)
    else:
        print("Usage: python run_aiscream.py <filename> [--debug]") 