import sys
import os
import re
import readline
import time
import threading

#############################
# Lexer Implementation
#############################

class Token:
    def __init__(self, type, value, lineno=None):
        self.type = type
        self.value = value
        self.lineno = lineno
        
    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)})"

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.lineno = 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None
        
    def error(self, message):
        raise Exception(f"Lexer error at line {self.lineno}: {message}")
        
    def advance(self):
        if self.current_char == '\n':
            self.lineno += 1
        self.pos += 1
        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]
        else:
            self.current_char = None
            
    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()
            
    def skip_comment(self):
        # Skip the first '/'
        self.advance()
        # Skip the second '/'
        self.advance()
        # Skip until end of line or end of file
        while self.current_char is not None and self.current_char != '\n':
            self.advance()
            
    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos < len(self.text):
            return self.text[peek_pos]
        return None
    
    def get_number(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)
    
    def get_string(self):
        quote_char = self.current_char  # can be ' or "
        result = ''
        self.advance()  # skip opening quote
        while self.current_char is not None and self.current_char != quote_char:
            if self.current_char == '\\' and self.peek() == quote_char:
                result += quote_char
                self.advance()
                self.advance()
            else:
                result += self.current_char
                self.advance()
        if self.current_char != quote_char:
            self.error("Unterminated string literal")
        self.advance()  # skip closing quote
        return result
    
    def get_identifier(self):
        result = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        return result
    
    def get_next_token(self):
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
                    'times': 'TIMES',  # Added 'times' keyword
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
            
        return Token('EOF', None)

#############################
# Parser Implementation
#############################

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        self.symbol_table = {}
        self.function_table = {}
        self.struct_table = {}
        
    def error(self, message):
        raise Exception(f"Parser error at line {self.lexer.lineno}: {message}")
        
    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(f"Expected {token_type}, got {self.current_token.type}")
            
    def program(self):
        """program : statement_list"""
        statements = self.statement_list()
        return ('program', statements)
        
    def statement_list(self):
        """statement_list : statement_list statement
                          | statement"""
        statements = []
        while self.current_token.type != 'EOF' and self.current_token.type != 'RBRACE':
            statements.append(self.statement())
        return statements
        
    def statement(self):
        """statement : simple_statement SEMICOLON
                     | compound_statement SEMICOLON
                     | compound_statement"""
        if self.current_token.type in ('DEF', 'IF', 'WHILE', 'FOR', 'STRUCT', 'CLASS', 'PARALLEL', 'REPEAT'):
            stmt = self.compound_statement()
            if self.current_token.type == 'SEMICOLON':
                self.eat('SEMICOLON')
            return stmt
        else:
            stmt = self.simple_statement()
            # Make the semicolon optional
            if self.current_token.type == 'SEMICOLON':
                self.eat('SEMICOLON')
            return stmt
            
    def simple_statement(self):
        """simple_statement : let_declaration
                           | const_declaration
                           | assignment
                           | print_statement
                           | return_statement
                           | expression"""
        if self.current_token.type == 'LET':
            return self.let_declaration()
        elif self.current_token.type == 'CONST':
            return self.const_declaration()
        elif self.current_token.type == 'ID':
            # Check for assignment
            if self.peek().type == 'EQUALS':
                return self.assignment()
            # Check for array assignment
            elif self.peek().type == 'LBRACKET':
                # Save state
                saved_pos = self.lexer.pos
                saved_lineno = self.lexer.lineno
                saved_current_char = self.lexer.current_char
                saved_token = self.current_token
                
                try:
                    var_name = self.current_token.value
                    self.eat('ID')
                    self.eat('LBRACKET')
                    self.expression()  # We don't need to capture the index yet
                    self.eat('RBRACKET')
                    if self.current_token.type == 'EQUALS':
                        # It's an array assignment, restore state and use assignment method
                        self.lexer.pos = saved_pos
                        self.lexer.lineno = saved_lineno
                        self.lexer.current_char = saved_current_char
                        self.current_token = saved_token
                        return self.assignment()
                except:
                    pass
                
                # Restore state for other expressions
                self.lexer.pos = saved_pos
                self.lexer.lineno = saved_lineno
                self.lexer.current_char = saved_current_char
                self.current_token = saved_token
            
        if self.current_token.type == 'PRINT':
            return self.print_statement()
        elif self.current_token.type == 'RETURN':
            return self.return_statement()
        else:
            return self.expression()
            
    def peek(self):
        # Save current state
        saved_pos = self.lexer.pos
        saved_lineno = self.lexer.lineno
        saved_current_char = self.lexer.current_char
        saved_token = self.current_token
        
        # Get next token
        next_token = self.lexer.get_next_token()
        
        # Restore state
        self.lexer.pos = saved_pos
        self.lexer.lineno = saved_lineno
        self.lexer.current_char = saved_current_char
        self.current_token = saved_token
        
        return next_token
        
    def compound_statement(self):
        """compound_statement : function_def
                             | if_statement
                             | while_loop
                             | for_loop
                             | struct_def
                             | class_def
                             | parallel_block
                             | repeat_loop"""
        token = self.current_token
        if token.type == 'DEF':
            return self.function_def()
        elif token.type == 'IF':
            return self.if_statement()
        elif token.type == 'WHILE':
            return self.while_loop()
        elif token.type == 'FOR':
            return self.for_loop()
        elif token.type == 'STRUCT':
            return self.struct_def()
        elif token.type == 'CLASS':
            return self.class_def()
        elif token.type == 'PARALLEL':
            return self.parallel_block()
        elif token.type == 'REPEAT':
            return self.repeat_loop()
        else:
            self.error(f"Unexpected token {token.type} in compound statement")
    
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
            
    # Additional methods of Parser class...
    # [Include all other Parser methods here from the original implementation]
    
    # For brevity, not all methods are included here. The real implementation would include:
    # return_statement, assignment, declaration, function_def, param_list, if_statement, 
    # while_loop, for_loop, print_statement, etc.

    def parallel_block(self):
        """parallel_block : PARALLEL LBRACE statement_list RBRACE"""
        self.eat('PARALLEL')
        self.eat('LBRACE')
        statements = self.statement_list()
        self.eat('RBRACE')
        return ('parallel', statements)
        
    def array_literal(self):
        """array_literal : LBRACKET (expression (COMMA expression)*)? RBRACKET"""
        self.eat('LBRACKET')
        elements = []
        
        # Empty array
        if self.current_token.type == 'RBRACKET':
            self.eat('RBRACKET')
            return ('array', elements)
            
        # Non-empty array
        elements.append(self.expression())
        
        while self.current_token.type == 'COMMA':
            self.eat('COMMA')
            elements.append(self.expression())
            
        self.eat('RBRACKET')
        return ('array', elements)
        
    def parse(self):
        return self.program()

#############################
# Interpreter Implementation
#############################

class ReturnValue(Exception):
    def __init__(self, value):
        self.value = value

class Interpreter:
    def __init__(self, parser, debug=False):
        self.parser = parser
        self.symbol_table = parser.symbol_table
        self.function_table = parser.function_table
        self.struct_table = parser.struct_table
        self.debug = debug
        
    def debug_print(self, message):
        if self.debug:
            print(f"[DEBUG] {message}")
            
    def evaluate(self, node, local_symbols=None):
        if local_symbols is None:
            local_symbols = {}
            
        if isinstance(node, tuple):
            ntype = node[0]
            if self.debug:
                self.debug_print(f"Evaluating node: {ntype}")
                
            if ntype == 'program':
                result = None
                for stmt in node[1]:
                    result = self.evaluate(stmt, local_symbols)
                return result
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
            # Other node types...
            # [Include all other node type handlers from the original implementation]
            
        else:
            return node
            
    def interpret(self):
        tree = self.parser.parse()
        return self.evaluate(tree)

#############################
# Function to run a Chan file
#############################

def run_file(filename, debug=False):
    """Run a Chan program from a file."""
    try:
        with open(filename, 'r') as file:
            text = file.read()
            
        if debug:
            print("[DEBUG] Running in debug mode")
            print("[DEBUG] File contents:")
            print("-------------------")
            print(text)
            print("-------------------")
            
        # Initialize tables
        symbol_table = {}
        function_table = {}
        struct_table = {}
        
        # Create lexer, parser and interpreter
        lexer = Lexer(text)
        if debug:
            print("\n[DEBUG] Tokenizing...")
            tokens = []
            while True:
                token = lexer.get_next_token()
                tokens.append(token)
                if token.type == 'EOF':
                    break
            print("Tokens:", tokens)
            lexer = Lexer(text)  # Reset lexer for parser
            
        parser = Parser(lexer)
        parser.symbol_table = symbol_table
        parser.function_table = function_table
        parser.struct_table = struct_table
        
        if debug:
            print("\n[DEBUG] Parsing...")
        result = parser.parse()
        if debug:
            print("AST:", result)
            print("\n[DEBUG] Executing...")
            
        interpreter = Interpreter(parser, debug=debug)
        interpreter.symbol_table = symbol_table
        interpreter.function_table = function_table
        interpreter.struct_table = struct_table
        
        interpreter.evaluate(result)
        
        if debug:
            print("\n[DEBUG] Final symbol table:", symbol_table)
            print("[DEBUG] Execution completed")
        
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
    except Exception as e:
        print(f"Error: {e}")

# Main function to run the interpreter
if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Run file if provided as argument
        debug_mode = '--debug' in sys.argv
        filename = sys.argv[1] if sys.argv[1] != '--debug' else sys.argv[2]
        run_file(filename, debug=debug_mode)
    else:
        print("Usage: python repeat_feature.py [--debug] <filename>")
        print("Example: python repeat_feature.py repeat_demo.chan") 