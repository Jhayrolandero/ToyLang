#!/usr/bin/env python3
"""
Chan Language Interpreter with Repeat Loop Feature
This is a simplified version of the Chan language interpreter that
supports the 'repeat' loop feature.
"""

import sys
import re

# Token types
TOKEN_TYPES = {
    'NUMBER': 'NUMBER',
    'STRING': 'STRING',
    'ID': 'ID',
    'PRINT': 'PRINT',
    'SEMICOLON': 'SEMICOLON',
    'LPAREN': 'LPAREN',
    'RPAREN': 'RPAREN',
    'LBRACE': 'LBRACE',
    'RBRACE': 'RBRACE',
    'REPEAT': 'REPEAT',
    'TIMES': 'TIMES',
    'EOF': 'EOF'
}

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
                return Token(TOKEN_TYPES['STRING'], self.get_string(), self.lineno)
                
            if self.current_char.isdigit():
                return Token(TOKEN_TYPES['NUMBER'], self.get_number(), self.lineno)
                
            if self.current_char.isalpha() or self.current_char == '_':
                identifier = self.get_identifier()
                # Check if it's a reserved word
                if identifier == 'print':
                    return Token(TOKEN_TYPES['PRINT'], identifier, self.lineno)
                elif identifier == 'repeat':
                    return Token(TOKEN_TYPES['REPEAT'], identifier, self.lineno)
                elif identifier == 'times':
                    return Token(TOKEN_TYPES['TIMES'], identifier, self.lineno)
                return Token(TOKEN_TYPES['ID'], identifier, self.lineno)
                
            # Single-character tokens
            if self.current_char == '(':
                self.advance()
                return Token(TOKEN_TYPES['LPAREN'], '(', self.lineno)
                
            if self.current_char == ')':
                self.advance()
                return Token(TOKEN_TYPES['RPAREN'], ')', self.lineno)
                
            if self.current_char == '{':
                self.advance()
                return Token(TOKEN_TYPES['LBRACE'], '{', self.lineno)
                
            if self.current_char == '}':
                self.advance()
                return Token(TOKEN_TYPES['RBRACE'], '}', self.lineno)
                
            if self.current_char == ';':
                self.advance()
                return Token(TOKEN_TYPES['SEMICOLON'], ';', self.lineno)
                
            self.error(f"Invalid character '{self.current_char}'")
            
        return Token(TOKEN_TYPES['EOF'], None, self.lineno)

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        
    def error(self, message):
        raise Exception(f"Parser error at line {self.current_token.lineno}: {message}")
        
    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(f"Expected {token_type}, got {self.current_token.type}")
            
    def program(self):
        """program : statement_list"""
        statements = self.statement_list()
        return statements
        
    def statement_list(self):
        """statement_list : statement*"""
        statements = []
        while self.current_token.type != TOKEN_TYPES['EOF']:
            statements.append(self.statement())
        return statements
        
    def statement(self):
        """statement : print_statement
                     | repeat_loop
                     | other_statement"""
        if self.current_token.type == TOKEN_TYPES['PRINT']:
            return self.print_statement()
        elif self.current_token.type == TOKEN_TYPES['REPEAT']:
            return self.repeat_loop()
        else:
            # Skip other statements for simplicity
            self.error(f"Unsupported statement type: {self.current_token.type}")
            
    def print_statement(self):
        """print_statement : PRINT LPAREN expression RPAREN SEMICOLON?"""
        self.eat(TOKEN_TYPES['PRINT'])
        self.eat(TOKEN_TYPES['LPAREN'])
        expr = self.expression()
        self.eat(TOKEN_TYPES['RPAREN'])
        
        # Optional semicolon
        if self.current_token.type == TOKEN_TYPES['SEMICOLON']:
            self.eat(TOKEN_TYPES['SEMICOLON'])
            
        return ('print', expr)
        
    def repeat_loop(self):
        """repeat_loop : REPEAT expression TIMES LBRACE statement_list RBRACE"""
        self.eat(TOKEN_TYPES['REPEAT'])
        
        # Parse the number of repetitions
        count = self.expression()
        
        # Parse the 'times' keyword
        self.eat(TOKEN_TYPES['TIMES'])
        
        # Parse the block
        self.eat(TOKEN_TYPES['LBRACE'])
        statements = []
        
        # Parse statements until we reach the closing brace
        while self.current_token.type != TOKEN_TYPES['RBRACE'] and self.current_token.type != TOKEN_TYPES['EOF']:
            statements.append(self.statement())
            
        self.eat(TOKEN_TYPES['RBRACE'])
        
        return ('repeat', count, statements)
        
    def expression(self):
        """expression : NUMBER
                      | STRING"""
        token = self.current_token
        
        if token.type == TOKEN_TYPES['NUMBER']:
            self.eat(TOKEN_TYPES['NUMBER'])
            return ('number', token.value)
        elif token.type == TOKEN_TYPES['STRING']:
            self.eat(TOKEN_TYPES['STRING'])
            return ('string', token.value)
        else:
            self.error(f"Expected expression, got {token.type}")
            
    def parse(self):
        return self.program()

class Interpreter:
    def __init__(self, parser):
        self.parser = parser
        
    def visit(self, node):
        if isinstance(node, tuple):
            node_type = node[0]
            
            if node_type == 'print':
                value = self.visit(node[1])
                print(value)
                return value
                
            elif node_type == 'repeat':
                count_node = node[1]
                statements = node[2]
                
                # Evaluate the count
                count = self.visit(count_node)
                
                # Execute the block the specified number of times
                result = None
                for _ in range(count):
                    for stmt in statements:
                        result = self.visit(stmt)
                        
                return result
                
            elif node_type == 'number':
                return node[1]
                
            elif node_type == 'string':
                return node[1]
                
        elif isinstance(node, list):
            result = None
            for statement in node:
                result = self.visit(statement)
            return result
            
        return None
        
    def interpret(self):
        tree = self.parser.parse()
        return self.visit(tree)

def run_file(filename):
    try:
        with open(filename, 'r') as file:
            source_code = file.read()
            
        lexer = Lexer(source_code)
        parser = Parser(lexer)
        interpreter = Interpreter(parser)
        interpreter.interpret()
        
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        run_file(sys.argv[1])
    else:
        print("Usage: python repeat_loop_interpreter.py <filename>") 