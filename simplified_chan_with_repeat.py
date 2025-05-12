#!/usr/bin/env python3
"""
Chan Mini-Interpreter with Repeat Loop Support
"""

import sys

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
                    'print': 'PRINT',
                    'let': 'LET',
                    'repeat': 'REPEAT',
                    'times': 'TIMES',
                }
                if identifier in reserved:
                    return Token(reserved[identifier], identifier, self.lineno)
                return Token('ID', identifier, self.lineno)
                
            # Handle single-character tokens
            if self.current_char == '+':
                self.advance()
                return Token('PLUS', '+', self.lineno)
                
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
                
            if self.current_char == ';':
                self.advance()
                return Token('SEMICOLON', ';', self.lineno)
                
            self.error(f"Invalid character '{self.current_char}'")
            
        return Token('EOF', None, self.lineno)

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        self.symbol_table = {}
        
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
        return ('program', statements)
        
    def statement_list(self):
        """statement_list : statement*"""
        statements = []
        while self.current_token.type != 'EOF' and self.current_token.type != 'RBRACE':
            statements.append(self.statement())
        return statements
        
    def statement(self):
        """statement : print_statement | let_statement | repeat_loop | expression_statement"""
        if self.current_token.type == 'PRINT':
            return self.print_statement()
        elif self.current_token.type == 'LET':
            return self.let_statement()
        elif self.current_token.type == 'REPEAT':
            return self.repeat_loop()
        else:
            return self.expression_statement()
            
    def print_statement(self):
        """print_statement : PRINT LPAREN expression RPAREN (SEMICOLON)?"""
        self.eat('PRINT')
        self.eat('LPAREN')
        expr = self.expression()
        self.eat('RPAREN')
        
        # Optional semicolon
        if self.current_token.type == 'SEMICOLON':
            self.eat('SEMICOLON')
            
        return ('print', expr)
        
    def let_statement(self):
        """let_statement : LET ID EQUALS expression (SEMICOLON)?"""
        self.eat('LET')
        var_name = self.current_token.value
        self.eat('ID')
        self.eat('EQUALS')
        expr = self.expression()
        
        # Optional semicolon
        if self.current_token.type == 'SEMICOLON':
            self.eat('SEMICOLON')
            
        return ('let', var_name, expr)
        
    def repeat_loop(self):
        """repeat_loop : REPEAT expression TIMES LBRACE statement_list RBRACE"""
        self.eat('REPEAT')
        count_expr = self.expression()
        self.eat('TIMES')
        self.eat('LBRACE')
        statements = self.statement_list()
        self.eat('RBRACE')
        
        return ('repeat', count_expr, statements)
        
    def expression_statement(self):
        """expression_statement : expression (SEMICOLON)?"""
        expr = self.expression()
        
        # Optional semicolon
        if self.current_token.type == 'SEMICOLON':
            self.eat('SEMICOLON')
            
        return expr
        
    def expression(self):
        """expression : term ((PLUS) term)*"""
        node = self.term()
        
        while self.current_token.type == 'PLUS':
            token = self.current_token
            self.eat('PLUS')
            node = ('+', node, self.term())
            
        return node
        
    def term(self):
        """term : factor"""
        return self.factor()
        
    def factor(self):
        """factor : NUMBER | STRING | ID | LPAREN expression RPAREN"""
        token = self.current_token
        
        if token.type == 'NUMBER':
            self.eat('NUMBER')
            return ('number', token.value)
        elif token.type == 'STRING':
            self.eat('STRING')
            return ('string', token.value)
        elif token.type == 'ID':
            self.eat('ID')
            return ('var', token.value)
        elif token.type == 'LPAREN':
            self.eat('LPAREN')
            node = self.expression()
            self.eat('RPAREN')
            return node
        else:
            self.error(f"Unexpected token {token.type} in expression")
            
    def parse(self):
        return self.program()

class Interpreter:
    def __init__(self, parser):
        self.parser = parser
        self.symbol_table = parser.symbol_table
        
    def eval(self, node):
        if isinstance(node, tuple):
            ntype = node[0]
            
            if ntype == 'program':
                result = None
                for stmt in node[1]:
                    result = self.eval(stmt)
                return result
                
            elif ntype == 'print':
                value = self.eval(node[1])
                print(value)
                return value
                
            elif ntype == 'let':
                var_name = node[1]
                value = self.eval(node[2])
                self.symbol_table[var_name] = value
                return value
                
            elif ntype == 'repeat':
                count = self.eval(node[1])
                
                if not isinstance(count, int):
                    raise Exception("Repeat count must be an integer")
                
                if count < 0:
                    raise Exception("Repeat count cannot be negative")
                
                result = None
                for _ in range(count):
                    for stmt in node[2]:
                        result = self.eval(stmt)
                        
                return result
                
            elif ntype == '+':
                left = self.eval(node[1])
                right = self.eval(node[2])
                
                # Handle string concatenation
                if isinstance(left, str) or isinstance(right, str):
                    return str(left) + str(right)
                else:
                    return left + right
                    
            elif ntype == 'number':
                return node[1]
                
            elif ntype == 'string':
                return node[1]
                
            elif ntype == 'var':
                var_name = node[1]
                if var_name in self.symbol_table:
                    return self.symbol_table[var_name]
                else:
                    raise Exception(f"Undefined variable: {var_name}")
                    
            else:
                return node
                
        else:
            return node
            
    def interpret(self):
        tree = self.parser.parse()
        return self.eval(tree)

def run_file(filename):
    try:
        with open(filename, 'r') as file:
            text = file.read()
            
        lexer = Lexer(text)
        parser = Parser(lexer)
        interpreter = Interpreter(parser)
        interpreter.interpret()
        
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
    except Exception as e:
        print(f"Error: {e}")

def main():
    if len(sys.argv) > 1:
        run_file(sys.argv[1])
    else:
        print("Usage: python simplified_chan_with_repeat.py <filename>")

if __name__ == '__main__':
    main() 