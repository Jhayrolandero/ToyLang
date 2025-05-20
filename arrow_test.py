#!/usr/bin/env python3

def evaluate_expression(expr, env):
    """Simple evaluator for testing arrow functions"""
    if isinstance(expr, int):
        return expr
    elif isinstance(expr, str):
        return env.get(expr, expr)
    elif isinstance(expr, list) and expr[0] == '+':
        return evaluate_expression(expr[1], env) + evaluate_expression(expr[2], env)
    elif isinstance(expr, list) and expr[0] == 'call':
        func = evaluate_expression(expr[1], env)
        args = [evaluate_expression(arg, env) for arg in expr[2]]
        return func(*args)
    elif isinstance(expr, list) and expr[0] == 'arrow':
        params = expr[1]
        body = expr[2]
        
        def arrow_function(*args):
            if len(args) != len(params):
                raise Exception(f"Expected {len(params)} args, got {len(args)}")
            
            # Create function environment with parameters
            func_env = env.copy()
            for i, param in enumerate(params):
                func_env[param] = args[i]
            
            # Evaluate body in this environment
            result = evaluate_expression(body, func_env)
            print(f"Arrow function result: {result}")
            return result
        
        return arrow_function

def run_test():
    """Run a test using our simple arrow function implementation"""
    # Define a global environment
    global_env = {}
    
    # Define an arrow function: (x, y) => x + y
    arrow_expr = ['arrow', ['x', 'y'], ['+', 'x', 'y']]
    
    # Assign it to 'add' in the environment
    add_func = evaluate_expression(arrow_expr, global_env)
    global_env['add'] = add_func
    
    # Call the function with arguments (2, 3)
    call_expr = ['call', 'add', [2, 3]]
    result = evaluate_expression(call_expr, global_env)
    
    print(f"Final result: {result}")

if __name__ == "__main__":
    run_test() 