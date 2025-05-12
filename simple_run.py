import sys
from use_case import Lexer, Parser, Interpreter

def run_file(filename, debug=False):
    """Run a Chan program from a file with repeat loop support."""
    try:
        with open(filename, 'r') as file:
            text = file.read()
            
        # Add 'repeat' and 'times' to the reserved words dictionary
        lexer = Lexer(text)
        lexer.get_next_token.__globals__['reserved'] = {
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
            'const': 'CONST'
        }
        
        # Add the repeat_loop method to the Parser class
        def repeat_loop(self):
            """repeat_loop : REPEAT expression TIMES LBRACE statement_list RBRACE"""
            self.eat('REPEAT')
            count_expr = self.expression()
            self.eat('TIMES')
            self.eat('LBRACE')
            statements = self.statement_list()
            self.eat('RBRACE')
            return ('repeat', count_expr, statements)
        
        # Add the method to the Parser class
        Parser.repeat_loop = repeat_loop
        
        # Make sure compound_statement can handle repeat
        original_compound_statement = Parser.compound_statement
        
        def new_compound_statement(self):
            token = self.current_token
            if token.type == 'REPEAT':
                return self.repeat_loop()
            return original_compound_statement(self)
            
        Parser.compound_statement = new_compound_statement
        
        # Initialize parser and interpreter
        parser = Parser(lexer)
        interpreter = Interpreter(parser, debug=debug)
        
        # Add repeat handling to the interpreter
        def evaluate_with_repeat(self, node, local_symbols=None):
            if local_symbols is None:
                local_symbols = {}
                
            if isinstance(node, tuple):
                ntype = node[0]
                
                if ntype == 'repeat':
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
                        for stmt in node[2]:
                            result = self.evaluate(stmt, local_symbols)
                    
                    return result
                
                # Call the original evaluate for other node types
                return self.evaluate(node, local_symbols)
            else:
                return node
        
        # Patch the evaluate method
        original_evaluate = interpreter.evaluate
        
        def new_evaluate(self, node, local_symbols=None):
            if isinstance(node, tuple) and node[0] == 'repeat':
                if local_symbols is None:
                    local_symbols = {}
                
                # Evaluate the count expression
                count = original_evaluate(self, node[1], local_symbols)
                
                # Check if count is a number
                if not isinstance(count, int):
                    raise Exception("Repeat count must be an integer")
                
                # Check if count is non-negative
                if count < 0:
                    raise Exception("Repeat count cannot be negative")
                
                # Execute the statements multiple times
                result = None
                for _ in range(count):
                    for stmt in node[2]:
                        result = original_evaluate(self, stmt, local_symbols)
                
                return result
            else:
                return original_evaluate(self, node, local_symbols)
                
        interpreter.evaluate = new_evaluate
        
        # Parse and run the program
        result = parser.parse()
        return interpreter.evaluate(result)
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == '__main__':
    if len(sys.argv) > 1:
        run_file(sys.argv[1], debug='--debug' in sys.argv)
    else:
        print("Usage: python simple_run.py <filename> [--debug]") 