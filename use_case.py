import sys
import re
import readline
import os
import threading
import time

#############################
# AST Node Classes
#############################

class ASTNode:
    def __init__(self):
        pass

    def __repr__(self):
        return self.__class__.__name__

class Assign(ASTNode):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"Assign({self.left}, {self.right})"

class Add(ASTNode):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"Add({self.left}, {self.right})"

class Multiply(ASTNode):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"Multiply({self.left}, {self.right})"

class Variable(ASTNode):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

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
                    'times': 'TIMES',
                    'and': 'AND',
                    'or': 'OR',
                    'not': 'NOT',
                    'struct': 'STRUCT',
                    'true': 'BOOLEAN',
                    'false': 'BOOLEAN',
                    'class': 'CLASS',
                    'new': 'NEW',
                    'let': 'LET',
                    'const': 'CONST',
                    'null': 'NULL',
                    'this': 'THIS'
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
                
            self.error(f"Invalid token '{self.current_char}'")
            
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
            
    def return_statement(self):
        """return_statement : RETURN expression"""
        self.eat('RETURN')
        expr = self.expression()
        return ('return', expr)
        
    def assignment(self):
        """assignment : ID EQUALS expression
                      | ID LBRACKET expression RBRACKET EQUALS expression"""
        var_name = self.current_token.value
        self.eat('ID')
        
        # Array element assignment: array[index] = expr
        if self.current_token.type == 'LBRACKET':
            self.eat('LBRACKET')
            index = self.expression()
            self.eat('RBRACKET')
            self.eat('EQUALS')
            expr = self.expression()
            return ('array_assign', var_name, index, expr)
        # Regular assignment
        else:
            self.eat('EQUALS')
            expr = self.expression()
            return ('assign', var_name, expr)
        
    def declaration(self):
        """declaration : (LET | CONST) ID EQUALS expression"""
        is_const = self.current_token.type == 'CONST'
        self.eat(self.current_token.type)  # eat LET or CONST
        var_name = self.current_token.value
        self.eat('ID')
        self.eat('EQUALS')
        expr = self.expression()
        return ('declare', var_name, expr, is_const)
        
    def function_def(self):
        """function_def : DEF ID LPAREN param_list RPAREN LBRACE statement_list RBRACE"""
        self.eat('DEF')
        func_name = self.current_token.value
        self.eat('ID')
        self.eat('LPAREN')
        params = self.param_list()
        self.eat('RPAREN')
        self.eat('LBRACE')
        statements = self.statement_list()
        self.eat('RBRACE')
        
        # Store function in function table
        self.function_table[func_name] = ('func_def', func_name, params, statements)
        return ('func_def', func_name, params, statements)
        
    def param_list(self):
        """param_list : param_list COMMA ID
                      | ID
                      | empty"""
        params = []
        if self.current_token.type == 'RPAREN':
            return params
            
        param = self.current_token.value
        self.eat('ID')
        params.append(param)
        
        while self.current_token.type == 'COMMA':
            self.eat('COMMA')
            param = self.current_token.value
            self.eat('ID')
            params.append(param)
            
        return params
        
    def if_statement(self):
        """if_statement : IF LPAREN expression RPAREN LBRACE statement_list RBRACE
                        | IF LPAREN expression RPAREN LBRACE statement_list RBRACE ELSE LBRACE statement_list RBRACE"""
        self.eat('IF')
        self.eat('LPAREN')
        condition = self.expression()
        self.eat('RPAREN')
        self.eat('LBRACE')
        true_branch = self.statement_list()
        self.eat('RBRACE')
        
        false_branch = None
        if self.current_token.type == 'ELSE':
            self.eat('ELSE')
            self.eat('LBRACE')
            false_branch = self.statement_list()
            self.eat('RBRACE')
            
        return ('if', condition, true_branch, false_branch)
        
    def while_loop(self):
        """while_loop : WHILE LPAREN expression RPAREN LBRACE statement_list RBRACE"""
        self.eat('WHILE')
        self.eat('LPAREN')
        condition = self.expression()
        self.eat('RPAREN')
        self.eat('LBRACE')
        body = self.statement_list()
        self.eat('RBRACE')
        return ('while', condition, body)
        
    def for_loop(self):
        """for_loop : FOR LPAREN assignment SEMICOLON expression SEMICOLON assignment RPAREN LBRACE statement_list RBRACE"""
        self.eat('FOR')
        self.eat('LPAREN')
        init = self.assignment()
        self.eat('SEMICOLON')
        condition = self.expression()
        self.eat('SEMICOLON')
        update = self.assignment()
        self.eat('RPAREN')
        self.eat('LBRACE')
        body = self.statement_list()
        self.eat('RBRACE')
        return ('for', init, condition, update, body)
        
    def print_statement(self):
        """print_statement : PRINT LPAREN expression RPAREN"""
        token = self.current_token  # Store the token to get line number
        self.eat('PRINT')
        self.eat('LPAREN')
        expr = self.expression()
        self.eat('RPAREN')
        return ('print', expr, token.lineno)
        
    def input_statement(self):
        """input_statement : INPUT LPAREN (expression)? RPAREN"""
        token = self.current_token  # Store the token to get line number
        self.eat('INPUT')
        self.eat('LPAREN')
        
        prompt = None
        if self.current_token.type != 'RPAREN':
            prompt = self.expression()
            
        self.eat('RPAREN')
        return ('input', prompt, token.lineno)
        
    def parseint_statement(self):
        """parseint_statement : PARSEINT LPAREN expression RPAREN"""
        self.eat('PARSEINT')
        self.eat('LPAREN')
        expr = self.expression()
        self.eat('RPAREN')
        return ('parseint', expr)
        
    def struct_def(self):
        """struct_def : STRUCT ID LBRACE field_list RBRACE"""
        self.eat('STRUCT')
        struct_name = self.current_token.value
        self.eat('ID')
        self.eat('LBRACE')
        fields = self.field_list()
        self.eat('RBRACE')
        
        # Store struct in struct table
        self.struct_table[struct_name] = fields
        return ('struct_def', struct_name, fields)
        
    def field_list(self):
        """field_list : field_list COMMA ID
                      | ID"""
        fields = []
        field = self.current_token.value
        self.eat('ID')
        fields.append(field)
        
        while self.current_token.type == 'COMMA':
            self.eat('COMMA')
            field = self.current_token.value
            self.eat('ID')
            fields.append(field)
            
        return fields
        
    def expression(self):
        """expression : logical_or_expression"""
        return self.logical_or_expression()
        
    def logical_or_expression(self):
        """logical_or_expression : logical_and_expression (OR logical_and_expression)*"""
        node = self.logical_and_expression()
        
        while self.current_token.type == 'OR':
            token = self.current_token
            self.eat('OR')
            node = (token.value, node, self.logical_and_expression())
            
        return node
        
    def logical_and_expression(self):
        """logical_and_expression : equality_expression (AND equality_expression)*"""
        node = self.equality_expression()
        
        while self.current_token.type == 'AND':
            token = self.current_token
            self.eat('AND')
            node = (token.value, node, self.equality_expression())
            
        return node
        
    def equality_expression(self):
        """equality_expression : relational_expression ((EQ | NE) relational_expression)*"""
        node = self.relational_expression()
        
        while self.current_token.type in ('EQ', 'NE'):
            token = self.current_token
            self.eat(token.type)
            node = (token.value, node, self.relational_expression())
            
        return node
        
    def relational_expression(self):
        """relational_expression : additive_expression ((GT | LT | GE | LE) additive_expression)*"""
        node = self.additive_expression()
        
        while self.current_token.type in ('GT', 'LT', 'GE', 'LE'):
            token = self.current_token
            self.eat(token.type)
            node = (token.value, node, self.additive_expression())
            
        return node
        
    def additive_expression(self):
        """additive_expression : multiplicative_expression ((PLUS | MINUS) multiplicative_expression)*"""
        node = self.multiplicative_expression()
        
        while self.current_token.type in ('PLUS', 'MINUS'):
            token = self.current_token
            self.eat(token.type)
            node = (token.value, node, self.multiplicative_expression())
            
        return node
        
    def multiplicative_expression(self):
        """multiplicative_expression : unary_expression ((TIMES | DIVIDE) unary_expression)*"""
        node = self.unary_expression()
        
        while self.current_token.type in ('TIMES', 'DIVIDE'):
            token = self.current_token
            self.eat(token.type)
            node = (token.value, node, self.unary_expression())
            
        return node
        
    def unary_expression(self):
        """unary_expression : NOT unary_expression
                           | primary_expression"""
        if self.current_token.type == 'NOT':
            token = self.current_token
            self.eat('NOT')
            return (token.value, self.unary_expression())
        return self.primary_expression()
        
    def primary_expression(self):
        """primary_expression : NUMBER
                             | BOOLEAN
                             | STRING
                             | array_literal
                             | ID
                             | ID LPAREN arg_list RPAREN
                             | ID LBRACKET expression RBRACKET
                             | INPUT LPAREN (expression)? RPAREN
                             | PARSEINT LPAREN expression RPAREN
                             | LPAREN expression RPAREN
                             | primary_expression DOT ID
                             | primary_expression DOT ID LPAREN arg_list RPAREN
                             | NEW ID LPAREN arg_list RPAREN
                             | arrow_function"""
        token = self.current_token

        # Input expression
        if token.type == 'INPUT':
            return self.input_statement()
            
        # ParseInt expression
        if token.type == 'PARSEINT':
            return self.parseint_statement()
            
        # Array literal: [1, 2, 3]
        if token.type == 'LBRACKET':
            return self.array_literal()
        # Arrow function: (x, y) => ...
        elif token.type == 'LPAREN':
            # Save state
            saved_pos = self.lexer.pos
            saved_lineno = self.lexer.lineno
            saved_current_char = self.lexer.current_char
            saved_token = self.current_token

            self.eat('LPAREN')
            params = []
            while self.current_token.type == 'ID':
                params.append(self.current_token.value)
                self.eat('ID')
                if self.current_token.type == 'COMMA':
                    self.eat('COMMA')
            if self.current_token.type == 'RPAREN':
                self.eat('RPAREN')
                if self.current_token.type == 'ARROW':
                    self.eat('ARROW')
                    body = self.expression()
                    return ('arrow_func', params, body)
            # Not an arrow function, restore state
            self.lexer.pos = saved_pos
            self.lexer.lineno = saved_lineno
            self.lexer.current_char = saved_current_char
            self.current_token = saved_token
            self.eat('LPAREN')
            node = self.expression()
            self.eat('RPAREN')
            return node
        # Class instance creation: new Person()
        elif token.type == 'NEW':
            self.eat('NEW')
            class_name = self.current_token.value
            self.eat('ID')
            self.eat('LPAREN')
            args = self.arg_list()
            self.eat('RPAREN')
            return ('new', class_name, args)
        # Arrow function: x => ...
        elif token.type == 'ID':
            id_name = token.value
            self.eat('ID')
            if self.current_token.type == 'ARROW':
                self.eat('ARROW')
                body = self.expression()
                return ('arrow_func', [id_name], body)
            # Check for function call
            if self.current_token.type == 'LPAREN':
                self.eat('LPAREN')
                args = self.arg_list()
                self.eat('RPAREN')
                return ('func_call', id_name, args)
            # Check for array access
            elif self.current_token.type == 'LBRACKET':
                self.eat('LBRACKET')
                index = self.expression()
                self.eat('RBRACKET')
                return ('array_access', ('var', id_name), index)
            # Check for field access
            elif self.current_token.type == 'DOT':
                self.eat('DOT')
                field = self.current_token.value
                self.eat('ID')
                
                # Check for method call
                if self.current_token.type == 'LPAREN':
                    self.eat('LPAREN')
                    args = self.arg_list()
                    self.eat('RPAREN')
                    return ('method_call', ('var', id_name), field, args)
                else:
                    return ('field_access', ('var', id_name), field)
            else:
                return ('var', id_name)
        elif token.type == 'NUMBER':
            self.eat('NUMBER')
            return ('number', token.value)
        elif token.type == 'BOOLEAN':
            self.eat('BOOLEAN')
            return ('boolean', token.value)
        elif token.type == 'STRING':
            self.eat('STRING')
            return ('string', token.value)
        elif token.type == 'NULL':
            self.eat('NULL')
            return ('null', None)
        else:
            self.error(f"Unexpected token {token.type} in expression")
            
    def arg_list(self):
        """arg_list : arg_list COMMA expression
                    | expression
                    | empty"""
        args = []
        if self.current_token.type == 'RPAREN':
            return args
            
        args.append(self.expression())
        
        while self.current_token.type == 'COMMA':
            self.eat('COMMA')
            args.append(self.expression())
            
        return args
        
    def class_def(self):
        """class_def : CLASS ID LBRACE method_list RBRACE"""
        self.eat('CLASS')
        class_name = self.current_token.value
        self.eat('ID')
        self.eat('LBRACE')
        methods = self.method_list()
        self.eat('RBRACE')
        
        # Store class in function table with special prefix
        self.function_table[f"__class_{class_name}"] = ('class_def', class_name, methods)
        return ('class_def', class_name, methods)
        
    def method_list(self):
        """method_list : method_list method
                      | method
                      | empty"""
        methods = []
        while self.current_token.type == 'ID':
            methods.append(self.method())
        return methods
        
    def method(self):
        """method : ID LPAREN param_list RPAREN LBRACE statement_list RBRACE"""
        method_name = self.current_token.value
        self.eat('ID')
        self.eat('LPAREN')
        params = self.param_list()
        self.eat('RPAREN')
        self.eat('LBRACE')
        statements = self.statement_list()
        self.eat('RBRACE')
        return ('method', method_name, params, statements)
        
    def let_declaration(self):
        """let_declaration : LET ID EQUALS expression"""
        self.eat('LET')
        var_name = self.current_token.value
        self.eat('ID')
        self.eat('EQUALS')
        expr = self.expression()
        return ('declare', var_name, expr, False)

    def const_declaration(self):
        """const_declaration : CONST ID EQUALS expression"""
        self.eat('CONST')
        var_name = self.current_token.value
        self.eat('ID')
        self.eat('EQUALS')
        expr = self.expression()
        return ('declare', var_name, expr, True)

    def arrow_function(self):
        """arrow_function : LPAREN param_list RPAREN ARROW expression"""
        self.eat('LPAREN')
        params = []
        while self.current_token.type == 'ID':
            params.append(self.current_token.value)
            self.eat('ID')
            if self.current_token.type == 'COMMA':
                self.eat('COMMA')
        self.eat('RPAREN')
        self.eat('ARROW')
        body = self.expression()
        return ('arrow_func', params, body)
        
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
        
    def parallel_block(self):
        """parallel_block : PARALLEL LBRACE statement_list RBRACE"""
        self.eat('PARALLEL')
        self.eat('LBRACE')
        statements = self.statement_list()
        self.eat('RBRACE')
        return ('parallel', statements)
        
    def repeat_loop(self):
        """repeat_loop : REPEAT expression TIMES LBRACE statement_list RBRACE"""
        token = self.current_token  # Store for error line tracking
        self.eat('REPEAT')
        
        # Parse the expression for the number of times to repeat - handle simple cases first
        if self.current_token.type == 'NUMBER':
            count_val = self.current_token.value
            self.eat('NUMBER')
            count_expr = ('number', count_val)
        elif self.current_token.type == 'ID':
            var_name = self.current_token.value
            self.eat('ID')
            count_expr = ('var', var_name)
        else:
            # Try for more complex expressions
            count_expr = self.expression()
        
        # Parse the "times" keyword
        if self.current_token.type != 'TIMES':
            self.error("Expected 'times' keyword in repeat loop")
        self.eat('TIMES')
        
        # Parse the block of code to repeat
        if self.current_token.type != 'LBRACE':
            self.error("Expected '{' after 'times' keyword in repeat loop")
        self.eat('LBRACE')
        
        statements = self.statement_list()
        
        if self.current_token.type != 'RBRACE':
            self.error("Expected '}' to close repeat loop")
        self.eat('RBRACE')
        
        return ('repeat', count_expr, statements)
        
    def parse(self):
        return self.program()

#############################
# Interpreter Implementation
#############################

class ToyLangError(Exception):
    """Custom exception class for ToyLang that includes line numbers"""
    def __init__(self, message, lineno=None):
        self.message = message
        self.lineno = lineno
        # Include line number in the main error message for better handling
        if lineno is not None:
            super().__init__(f"{message} (at line {lineno})")
        else:
            super().__init__(message)

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
        self.current_line = None
        self.file_lines = {}
        
    def debug_print(self, message):
        if self.debug:
            print(f"[DEBUG] {message}")
    
    def set_file_content(self, filename, content):
        """Store the file content for better error reporting"""
        self.filename = filename
        self.file_lines = content.splitlines()
    
    def track_line(self, node):
        """Extract line number information from a node if possible"""
        if isinstance(node, tuple) and len(node) > 1:
            # For print statements and other nodes with line number as the last element
            if len(node) > 2 and isinstance(node[-1], int):
                self.current_line = node[-1]
                return
            
            # For token-based line numbers
            if isinstance(node[1], Token) and node[1].lineno is not None:
                self.current_line = node[1].lineno
                return
                
            # For nodes with explicit lineno attribute
            elif hasattr(node, 'lineno') and node.lineno is not None:
                self.current_line = node.lineno
                return
                
        # Debug line tracking if debug mode is enabled
        if self.debug and self.current_line is not None:
            self.debug_print(f"Current line: {self.current_line}")

    def evaluate(self, node, local_symbols=None):
        if local_symbols is None:
            local_symbols = {}
        
        # Try to extract line number from node
        self.track_line(node)
            
        if isinstance(node, tuple):
            ntype = node[0]
            if self.debug:
                self.debug_print(f"Evaluating node: {ntype}")
                if ntype in ('assign', 'declare', 'print', 'if', 'while', 'for'):
                    self.debug_print(f"  Node details: {node}")
            
            if ntype == 'program':
                result = None
                for stmt in node[1]:
                    result = self.evaluate(stmt, local_symbols)
                return result
            elif ntype == 'assign':
                var = node[1]
                val = self.evaluate(node[2], local_symbols)
                if self.debug:
                    self.debug_print(f"  Assigning {val} to {var}")
                # Check if variable is const
                if var in self.symbol_table and isinstance(self.symbol_table[var], tuple) and self.symbol_table[var][1]:
                    raise Exception(f"Cannot reassign constant variable '{var}'")
                
                # Special handling for null: remove from symbol table to allow redeclaration
                if val is None:
                    if var in local_symbols:
                        del local_symbols[var]
                    if var in self.symbol_table:
                        del self.symbol_table[var]
                else:
                    local_symbols[var] = val
                    self.symbol_table[var] = val
                    
                return val
            elif ntype == 'array_assign':
                array_name = node[1]
                index = self.evaluate(node[2], local_symbols)
                value = self.evaluate(node[3], local_symbols)
                
                if self.debug:
                    self.debug_print(f"Array assign: {array_name}[{index}] = {value}")
                    self.debug_print(f"Local symbols: {local_symbols.keys()}")
                    self.debug_print(f"Symbol table: {self.symbol_table.keys()}")
                
                # Get the array
                self.current_context = 'array_access'
                try:
                    if array_name in local_symbols:
                        array = local_symbols[array_name]
                        if self.debug:
                            self.debug_print(f"Found in local_symbols: {array}")
                    elif array_name in self.symbol_table:
                        array = self.symbol_table[array_name]
                        if self.debug:
                            self.debug_print(f"Found in symbol_table: {array}")
                    else:
                        raise Exception(f"Undefined object: {array_name}")
                    
                    # Check if array is a tuple (const declaration)
                    if isinstance(array, tuple):
                        if array[1]:  # Check if const
                            raise Exception(f"Cannot modify constant array '{array_name}'")
                        array = array[0]  # Extract the actual array
                    
                    if not isinstance(array, list):
                        raise Exception(f"Object '{array_name}' is not an array")
                    if not isinstance(index, int):
                        raise Exception("Array index must be an integer")
                    if index < 0 or index >= len(array):
                        raise Exception(f"Array index {index} out of bounds (0-{len(array)-1})")
                    
                    # Update array element
                    array[index] = value
                    
                    # Update the array in the symbol tables
                    if array_name in local_symbols:
                        if isinstance(local_symbols[array_name], tuple):
                            local_symbols[array_name] = (array, local_symbols[array_name][1])
                        else:
                            local_symbols[array_name] = array
                    if array_name in self.symbol_table:
                        if isinstance(self.symbol_table[array_name], tuple):
                            self.symbol_table[array_name] = (array, self.symbol_table[array_name][1])
                        else:
                            self.symbol_table[array_name] = array
                    
                    return value
                finally:
                    self.current_context = 'variable'
            elif ntype == 'declare':
                var_name = node[1]
                is_const = node[3]
                
                # Check if variable is already declared (but allow if it was nullified)
                if (var_name in local_symbols or var_name in self.symbol_table):
                    raise Exception(f"Redeclaration error: Variable '{var_name}' has already been declared")
                    
                val = self.evaluate(node[2], local_symbols)
                
                # Store value with const flag
                local_symbols[var_name] = (val, is_const)
                self.symbol_table[var_name] = val  # Store just the value in the symbol table
                return val
            elif ntype == 'number':
                return node[1]
            elif ntype == 'boolean':
                return node[1]
            elif ntype == 'string':
                return node[1]
            elif ntype == 'null':
                return None
            elif ntype == 'var':
                var = node[1]
                if var in local_symbols:
                    val = local_symbols[var]
                    # Handle tuple case for const variables
                    if isinstance(val, tuple):
                        return val[0]
                    return val
                elif var in self.symbol_table:
                    val = self.symbol_table[var]
                    # Handle tuple case for const variables
                    if isinstance(val, tuple):
                        return val[0]
                    return val
                else:
                    # Check if this is an array access context (will be used in array_access)
                    parent_context = getattr(self, 'current_context', 'variable')
                    
                    # Debug output for line number information
                    if self.debug:
                        self.debug_print(f"Undefined variable '{var}' at line {self.current_line}")
                        
                    if parent_context == 'array_access':
                        raise ToyLangError(f"Undefined object: {var}", self.current_line)
                    else:
                        raise ToyLangError(f"Undefined variable: {var}", self.current_line)
            elif ntype in ('+', '-', '*', '/', '==', '!=', '>', '<', '>=', '<=', 'and', 'or'):
                left = self.evaluate(node[1], local_symbols)
                right = self.evaluate(node[2], local_symbols)
                if ntype == '+':
                    # Handle string concatenation with automatic conversion
                    if isinstance(left, str) and isinstance(right, (int, float)):
                        raise Exception(f"Type error: cannot add string and number")
                    elif isinstance(right, str) and isinstance(left, (int, float)):
                        raise Exception(f"Type error: cannot add number and string")
                    elif isinstance(left, str) or isinstance(right, str):
                        return str(left) + str(right)
                    else:
                        return left + right
                elif ntype == '-':
                    return left - right
                elif ntype == '*':
                    return left * right
                elif ntype == '/':
                    return left / right
                elif ntype == '==':
                    return left == right
                elif ntype == '!=':
                    return left != right
                elif ntype == '>':
                    return left > right
                elif ntype == '<':
                    return left < right
                elif ntype == '>=':
                    return left >= right
                elif ntype == '<=':
                    return left <= right
                elif ntype == 'and':
                    return left and right
                elif ntype == 'or':
                    return left or right
            elif ntype == 'not':
                return not self.evaluate(node[1], local_symbols)
            elif ntype == 'class_def':
                return None
            elif ntype == 'new':
                class_name = node[1]
                args = [self.evaluate(arg, local_symbols) for arg in node[2]]
                
                class_key = f"__class_{class_name}"
                if class_key not in self.function_table:
                    raise Exception(f"Undefined class: {class_name}")
                    
                class_def = self.function_table[class_key]
                methods = class_def[2]
                
                # Create instance with methods
                instance = {'__class__': class_name}
                for method in methods:
                    method_name = method[1]
                    method_params = method[2]
                    method_body = method[3]
                    
                    def create_method(method_name, method_params, method_body):
                        def method_func(*args):
                            if len(args) != len(method_params):
                                raise Exception(f"Method {method_name} expected {len(method_params)} arguments, got {len(args)}")
                            method_env = dict(zip(method_params, args))
                            # Add 'this' reference to the instance
                            method_env['this'] = instance
                            # Execute method body with method environment
                            try:
                                result = None
                                for stmt in method_body:
                                    result = self.evaluate(stmt, method_env)
                                return result
                            except ReturnValue as rv:
                                return rv.value
                        return method_func
                    
                    instance[method_name] = create_method(method_name, method_params, method_body)
                
                return instance
            elif ntype == 'method_call':
                obj = self.evaluate(node[1], local_symbols)
                method_name = node[2]
                args = [self.evaluate(arg, local_symbols) for arg in node[3]]
                
                if not isinstance(obj, dict) or method_name not in obj:
                    raise Exception(f"Method '{method_name}' not found in object")
                    
                method = obj[method_name]
                if not callable(method):
                    raise Exception(f"'{method_name}' is not a method")
                    
                return method(*args)
            elif ntype == 'func_def':
                return None
            elif ntype == 'if':
                cond = self.evaluate(node[1], local_symbols)
                if cond:
                    try:
                        result = None
                        for stmt in node[2]:
                            result = self.evaluate(stmt, local_symbols)
                        return result
                    except ReturnValue as rv:
                        return rv.value
                elif node[3] is not None:
                    try:
                        result = None
                        for stmt in node[3]:
                            result = self.evaluate(stmt, local_symbols)
                        return result
                    except ReturnValue as rv:
                        return rv.value
                else:
                    return None
            elif ntype == 'while':
                while self.evaluate(node[1], local_symbols):
                    try:
                        for stmt in node[2]:
                            self.evaluate(stmt, local_symbols)
                    except ReturnValue as rv:
                        return rv.value
                return None
            elif ntype == 'for':
                self.evaluate(node[1], local_symbols)  # initializer
                outputs = []
                while self.evaluate(node[2], local_symbols):
                    try:
                        result = None
                        for stmt in node[4]:
                            result = self.evaluate(stmt, local_symbols)
                        outputs.append(result)
                    except ReturnValue as rv:
                        outputs.append(rv.value)
                    self.evaluate(node[3], local_symbols)  # update
                return outputs
            elif ntype == 'print':
                val = self.evaluate(node[1], local_symbols)
                if len(node) > 2:
                    self.current_line = node[2]  # Extract line number
                    if self.debug:
                        self.debug_print(f"Setting current line to {self.current_line} from print statement")
                print(val)
                return val
            elif ntype == 'input':
                # If there's a prompt, evaluate and print it without a newline
                if node[1] is not None:
                    prompt = self.evaluate(node[1], local_symbols)
                    # Print without newline
                    print(prompt, end='', flush=True)
                
                if len(node) > 2:
                    self.current_line = node[2]  # Extract line number
                    
                # Get user input
                try:
                    user_input = input()
                    return user_input
                except EOFError:
                    return ""
            elif ntype == 'parseint':
                val = self.evaluate(node[1], local_symbols)
                try:
                    return int(val)
                except ValueError:
                    raise Exception(f"Cannot convert '{val}' to an integer")
            elif ntype == 'return':
                val = self.evaluate(node[1], local_symbols)
                raise ReturnValue(val)
            elif ntype == 'struct_def':
                return None
            elif ntype == 'field_access':
                obj = self.evaluate(node[1], local_symbols)
                field = node[2]
                
                if isinstance(obj, dict):
                    if field in obj:
                        # If the field is a method, return it without executing
                        if callable(obj[field]):
                            return obj[field]
                        return obj[field]
                    elif '__class__' in obj:
                        raise Exception(f"Field '{field}' not found in class {obj['__class__']}")
                    else:
                        raise Exception(f"Field '{field}' not found in object")
                else:
                    raise Exception(f"Field access on non-object type")
            elif ntype == 'arrow_func':
                params = node[1]
                body = node[2]
                
                # Create a closure function
                def arrow_function(*args):
                    if len(args) != len(params):
                        raise Exception(f"Arrow function expected {len(params)} arguments, got {len(args)}")
                    
                    # Create a new environment for the function execution
                    func_env = dict(zip(params, args))
                    # Include the outer scope in the closure
                    func_env.update(local_symbols)
                    
                    # Evaluate the body with this environment
                    return self.evaluate(body, func_env)
                
                return arrow_function
            elif ntype == 'array':
                elements = [self.evaluate(elem, local_symbols) for elem in node[1]]
                return elements
            elif ntype == 'array_access':
                # Set a flag to indicate we're in an array access context
                self.current_context = 'array_access'
                try:
                    array = self.evaluate(node[1], local_symbols)
                    index = self.evaluate(node[2], local_symbols)
                    
                    if not isinstance(array, list):
                        raise Exception("Cannot access index on non-array type")
                    if not isinstance(index, int):
                        raise Exception("Array index must be an integer")
                    if index < 0 or index >= len(array):
                        raise Exception(f"Array index {index} out of bounds (0-{len(array)-1})")
                        
                    return array[index]
                finally:
                    # Reset the context flag when done
                    self.current_context = 'variable'
            elif ntype == 'func_call':
                # Get the function name
                func_name = node[1]
                # Evaluate the arguments
                args = [self.evaluate(arg, local_symbols) for arg in node[2]]
                
                # Check if it's a method on an object
                if func_name in local_symbols and callable(local_symbols[func_name]):
                    return local_symbols[func_name](*args)
                elif func_name in self.symbol_table and callable(self.symbol_table[func_name]):
                    return self.symbol_table[func_name](*args)
                # Check the function table
                elif func_name in self.function_table:
                    # Get the function definition
                    func_def = self.function_table[func_name]
                    # Get parameters and body
                    params = func_def[2]
                    body = func_def[3]
                    
                    # Check if number of arguments matches parameters
                    if len(args) != len(params):
                        raise Exception(f"Function '{func_name}' expected {len(params)} arguments, got {len(args)}")
                    
                    # Create a new environment for the function call
                    func_locals = dict(zip(params, args))
                    
                    # Execute the function body
                    try:
                        result = None
                        for stmt in body:
                            result = self.evaluate(stmt, func_locals)
                        return result
                    except ReturnValue as rv:
                        return rv.value
                elif func_name == 'sleep':
                    # Built-in sleep function for demonstration
                    if len(args) != 1:
                        raise Exception("sleep() expects 1 argument (milliseconds)")
                    if not isinstance(args[0], (int, float)):
                        raise Exception("sleep() argument must be a number")
                    # Convert milliseconds to seconds for time.sleep
                    time.sleep(args[0] / 1000)
                    return None
                elif func_name == 'timestamp':
                    # Built-in timestamp function that returns current time in seconds
                    return time.time()
                elif func_name == 'delete':
                    # Built-in delete function to remove variables
                    if len(args) != 1:
                        raise Exception("delete() expects 1 argument (variable name)")
                    
                    # Get the variable name directly from the AST node
                    # The argument to delete should be the name of the variable without evaluation
                    if len(node[2]) != 1:
                        raise Exception("delete() expects 1 argument")
                        
                    arg_node = node[2][0]
                    if arg_node[0] != 'var':
                        raise Exception("delete() argument must be a variable name")
                        
                    var_name = arg_node[1]  # Extract the variable name from the 'var' node
                    
                    # Remove variable from both symbol tables
                    if var_name in local_symbols:
                        del local_symbols[var_name]
                    if var_name in self.symbol_table:
                        del self.symbol_table[var_name]
                    return None
                elif f"__class_{func_name}" in self.function_table:
                    # It's a class constructor call
                    class_def = self.function_table[f"__class_{func_name}"]
                    raise Exception("Class constructor must be called with 'new' keyword")
                elif func_name in self.struct_table:
                    # It's a struct constructor call
                    fields = self.struct_table[func_name]
                    if len(args) != len(fields):
                        raise Exception(f"Struct {func_name} expects {len(fields)} fields, got {len(args)}")
                    
                    # Create a new struct instance (a dictionary with field names as keys)
                    instance = {}
                    for i, field in enumerate(fields):
                        instance[field] = args[i]
                    return instance
                else:
                    raise Exception(f"Function '{func_name}' is not defined")
            elif ntype == 'parallel':
                # Create a separate thread to execute the block
                block_results = []
                
                # Function to run statements in a thread
                def execute_block():
                    try:
                        # Create a copy of the local symbols
                        thread_locals = local_symbols.copy() if local_symbols else {}
                        
                        # Execute each statement in the block
                        result = None
                        for stmt in node[1]:
                            result = self.evaluate(stmt, thread_locals)
                        
                        # Store the last result
                        block_results.append(result)
                        
                        # Update main thread's symbol table
                        for key, value in thread_locals.items():
                            if key in self.symbol_table:
                                self.symbol_table[key] = value
                    except Exception as e:
                        print(f"Error in parallel execution: {e}")
                
                # Create and start thread
                thread = threading.Thread(target=execute_block)
                thread.start()
                
                # Don't wait for thread to complete
                # This is what makes execution parallel
                # The thread continues in the background
                
                # Return None immediately
                return None
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
                for _ in range(count):
                    try:
                        for stmt in node[2]:
                            self.evaluate(stmt, local_symbols)
                    except ReturnValue as rv:
                        return rv.value
                
                # Return None instead of the last result
                return None
            else:
                raise Exception(f"Unknown node type: {ntype}")
        else:
            return node
            
    def interpret(self):
        tree = self.parser.parse()
        return self.evaluate(tree)

#############################
# REPL (Read-Eval-Print Loop)
#############################

def run_file(filename, debug=False, verbose=False, trace=False):
    """Run a ToyLang program from a file."""
    try:
        with open(filename, 'r') as file:
            text = file.read()
            
        if debug or trace:
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
        if debug or trace:
            print("\n[DEBUG] Tokenizing...")
            tokens = []
            while True:
                token = lexer.get_next_token()
                tokens.append(token)
                if token.type == 'EOF':
                    break
            print("Token Stream:")
            for token in tokens:
                print(f"  {token}")
            lexer = Lexer(text)  # Reset lexer for parser
            
        parser = Parser(lexer)
        parser.symbol_table = symbol_table
        parser.function_table = function_table
        parser.struct_table = struct_table
        
        if debug or verbose or trace:
            print("\n[DEBUG] Parsing...")
        result = parser.parse()
        if debug or verbose or trace:
            print("AST:", result)
            if verbose:
                return  # Exit after showing AST in verbose mode
            print("\n[DEBUG] Executing...")
            
        interpreter = Interpreter(parser, debug=debug or trace)
        interpreter.symbol_table = symbol_table
        interpreter.function_table = function_table
        interpreter.struct_table = struct_table
        interpreter.set_file_content(filename, text)  # Pass file content for error reporting
        
        if trace:
            print("\n[TRACE] Evaluation Steps:")
            print("-------------------")
            
        interpreter.evaluate(result)
        
        if debug or trace:
            print("\n[DEBUG] Final symbol table:", symbol_table)
            print("[DEBUG] Execution completed")
        
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
    except Exception as e:
        # Add line number information to the exception message if available
        if hasattr(e, 'lineno') and e.lineno is not None:
            print(f"Error at line {e.lineno}: {str(e)}")
        else:
            print(f"Error: {str(e)}")
        
        # Print file context if line number is available
        if hasattr(e, 'lineno') and e.lineno is not None:
            try:
                with open(filename, 'r') as f:
                    lines = f.readlines()
                
                if 1 <= e.lineno <= len(lines):
                    # Show the line with the error
                    print(f"Line {e.lineno}: {lines[e.lineno-1].strip()}")
            except:
                pass  # If we can't read the file, just continue

def main():
    if len(sys.argv) > 1:
        # Run file if provided as argument
        if sys.argv[1] == 'run' and len(sys.argv) > 2:
            run_file(sys.argv[2])
        else:
            print("Usage: python use_case.py run <filename>")
    else:
        # Start REPL if no arguments
        print("Enter your code (type 'exit' to quit):")
        print("Use Up/Down arrows for command history, Left/Right for cursor movement")

        # Set up readline for command history
        histfile = os.path.join(os.path.expanduser("~"), ".chan_history")
        try:
            readline.read_history_file(histfile)
            # Set history file size
            readline.set_history_length(1000)
        except FileNotFoundError:
            pass

        # Persistent symbol/function/struct tables
        symbol_table = {}
        function_table = {}
        struct_table = {}

        while True:
            try:
                text = input('>>> ')
                if text.strip().lower() == 'exit':
                    # Save history before exiting
                    readline.write_history_file(histfile)
                    break
                if not text.strip():
                    continue

                lexer = Lexer(text)
                # Always create a new parser and interpreter for each input
                parser = Parser(lexer)
                parser.symbol_table = symbol_table
                parser.function_table = function_table
                parser.struct_table = struct_table
                interpreter = Interpreter(parser)
                interpreter.symbol_table = symbol_table
                interpreter.function_table = function_table
                interpreter.struct_table = struct_table

                try:
                    result = parser.parse()
                    output = interpreter.evaluate(result)
                    if output is not None:
                        print(f"=> {output}")
                except Exception as e:
                    print(f"Error: {e}")

            except KeyboardInterrupt:
                print("\nExiting...")
                # Save history before exiting
                readline.write_history_file(histfile)
                break
            except EOFError:
                print("\nExiting...")
                # Save history before exiting
                readline.write_history_file(histfile)
                break

if __name__ == '__main__':
    main()