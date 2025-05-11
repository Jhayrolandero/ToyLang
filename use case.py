import sys
import re
import readline  # Add readline import for arrow key support

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
                    'and': 'AND',
                    'or': 'OR',
                    'not': 'NOT',
                    'struct': 'STRUCT',
                    'true': 'BOOLEAN',
                    'false': 'BOOLEAN',
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
        if self.current_token.type in ('DEF', 'IF', 'WHILE', 'FOR', 'STRUCT'):
            stmt = self.compound_statement()
            if self.current_token.type == 'SEMICOLON':
                self.eat('SEMICOLON')
            return stmt
        else:
            stmt = self.simple_statement()
            self.eat('SEMICOLON')
            return stmt
            
    def simple_statement(self):
        """simple_statement : declaration
                           | assignment
                           | print_statement
                           | return_statement
                           | expression"""
        # Check for declaration (LET/CONST ID)
        if self.current_token.type in ('LET', 'CONST'):
            return self.declaration()
                
        if self.current_token.type == 'ID' and self.peek().type == 'EQUALS':
            # Check if variable is declared before assignment
            var_name = self.current_token.value
            if var_name not in self.symbol_table:
                self.error(f"Variable '{var_name}' must be declared with 'let' or 'const' before use")
            return self.assignment()
        elif self.current_token.type == 'PRINT':
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
                             | struct_def"""
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
        else:
            self.error(f"Unexpected token {token.type} in compound statement")
            
    def return_statement(self):
        """return_statement : RETURN expression"""
        self.eat('RETURN')
        expr = self.expression()
        return ('return', expr)
        
    def assignment(self):
        """assignment : ID EQUALS expression"""
        var_name = self.current_token.value
        self.eat('ID')
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
        self.eat('PRINT')
        self.eat('LPAREN')
        expr = self.expression()
        self.eat('RPAREN')
        return ('print', expr)
        
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
                             | ID
                             | ID LPAREN arg_list RPAREN
                             | LPAREN expression RPAREN
                             | primary_expression DOT ID"""
        token = self.current_token
        
        if token.type == 'NUMBER':
            self.eat('NUMBER')
            return ('number', token.value)
        elif token.type == 'BOOLEAN':
            self.eat('BOOLEAN')
            return ('boolean', token.value)
        elif token.type == 'STRING':
            self.eat('STRING')
            return ('string', token.value)
        elif token.type == 'LPAREN':
            self.eat('LPAREN')
            node = self.expression()
            self.eat('RPAREN')
            return node
        elif token.type == 'ID':
            # Could be variable, function call, or field access
            id_name = token.value
            self.eat('ID')
            
            # Check for function call
            if self.current_token.type == 'LPAREN':
                self.eat('LPAREN')
                args = self.arg_list()
                self.eat('RPAREN')
                return ('func_call', id_name, args)
            # Check for field access
            elif self.current_token.type == 'DOT':
                self.eat('DOT')
                field = self.current_token.value
                self.eat('ID')
                return ('field_access', ('var', id_name), field)
            else:
                return ('var', id_name)
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
        
    def parse(self):
        return self.program()

#############################
# Interpreter Implementation
#############################

class ReturnValue(Exception):
    def __init__(self, value):
        self.value = value

class Interpreter:
    def __init__(self, parser):
        self.parser = parser
        self.symbol_table = parser.symbol_table
        self.function_table = parser.function_table
        self.struct_table = parser.struct_table
        
    def evaluate(self, node, local_symbols=None):
        if local_symbols is None:
            local_symbols = {}
            
        if isinstance(node, tuple):
            ntype = node[0]
            if ntype == 'program':
                result = None
                for stmt in node[1]:
                    result = self.evaluate(stmt, local_symbols)
                return result
            elif ntype == 'assign':
                var = node[1]
                val = self.evaluate(node[2], local_symbols)
                # Check if variable is const
                if var in self.symbol_table and isinstance(self.symbol_table[var], tuple) and self.symbol_table[var][1]:
                    raise Exception(f"Cannot reassign constant variable '{var}'")
                local_symbols[var] = val
                self.symbol_table[var] = val
                return val
            elif ntype == 'declare':
                var_name = node[1]
                is_const = node[3]
                # Check if variable is already declared
                if var_name in local_symbols or var_name in self.symbol_table:
                    raise Exception(f"Redeclaration error: Variable '{var_name}' has already been declared")
                val = self.evaluate(node[2], local_symbols)
                # Store value with const flag
                local_symbols[var_name] = (val, is_const)
                self.symbol_table[var_name] = (val, is_const)
                return val
            elif ntype == 'number':
                return node[1]
            elif ntype == 'boolean':
                return node[1]
            elif ntype == 'string':
                return node[1]
            elif ntype == 'var':
                var = node[1]
                if var in local_symbols:
                    val = local_symbols[var]
                    return val[0] if isinstance(val, tuple) else val
                elif var in self.symbol_table:
                    val = self.symbol_table[var]
                    return val[0] if isinstance(val, tuple) else val
                else:
                    raise Exception(f"Undefined variable: {var}")
            elif ntype in ('+', '-', '*', '/', '==', '!=', '>', '<', '>=', '<='):
                left = self.evaluate(node[1], local_symbols)
                right = self.evaluate(node[2], local_symbols)
                if ntype == '+':
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
                return self.evaluate(node[1], local_symbols) and self.evaluate(node[2], local_symbols)
            elif ntype == 'or':
                return self.evaluate(node[1], local_symbols) or self.evaluate(node[2], local_symbols)
            elif ntype == 'not':
                return not self.evaluate(node[1], local_symbols)
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
                print(val)
                return val
            elif ntype == 'func_def':
                return None
            elif ntype == 'func_call':
                func_name = node[1]
                args = [self.evaluate(arg, local_symbols) for arg in node[2]]
                
                if func_name in self.struct_table:
                    fields = self.struct_table[func_name]
                    if len(args) != len(fields):
                        raise Exception(f"Incorrect number of arguments for struct {func_name}")
                    return {'__struct__': func_name, **dict(zip(fields, args))}
                elif func_name in self.function_table:
                    func_def = self.function_table[func_name]
                    param_list = func_def[2]
                    stmts = func_def[3]
                    if len(args) != len(param_list):
                        raise Exception(f"Incorrect number of arguments for function '{func_name}'")
                    local_env = dict(zip(param_list, args))
                    try:
                        result = None
                        for stmt in stmts:
                            result = self.evaluate(stmt, local_env)
                    except ReturnValue as rv:
                        return rv.value
                    return result
                else:
                    raise Exception(f"Undefined function: {func_name}")
            elif ntype == 'return':
                val = self.evaluate(node[1], local_symbols)
                raise ReturnValue(val)
            elif ntype == 'struct_def':
                return None
            elif ntype == 'field_access':
                obj = self.evaluate(node[1], local_symbols)
                field = node[2]
                if isinstance(obj, dict) and field in obj:
                    return obj[field]
                else:
                    raise Exception(f"Field '{field}' not found in object")
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

def main():
    print("Enter your code (type 'exit' to quit):")

    # Persistent symbol/function/struct tables
    symbol_table = {}
    function_table = {}
    struct_table = {}
    parser = None
    interpreter = None

    # Enable readline for arrow key navigation
    readline.set_auto_history(True)

    while True:
        try:
            text = input('>>> ')
            if text.strip().lower() == 'exit':
                break
            if not text.strip():
                continue

            lexer = Lexer(text)
            if parser is None:
                parser = Parser(lexer)
                # Attach persistent tables
                parser.symbol_table = symbol_table
                parser.function_table = function_table
                parser.struct_table = struct_table
                interpreter = Interpreter(parser)
                interpreter.symbol_table = symbol_table
                interpreter.function_table = function_table
                interpreter.struct_table = struct_table
            else:
                parser.lexer = lexer
                parser.current_token = lexer.get_next_token()

            try:
                result = parser.parse()
                output = interpreter.evaluate(result)
                if output is not None:
                    print(f"=> {output}")
            except Exception as e:
                print(f"Error: {e}")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except EOFError:
            print("\nExiting...")
            break

if __name__ == '__main__':
    main()