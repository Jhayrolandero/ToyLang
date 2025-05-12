# Repeat Loop Feature for Chan Language

This repository includes an implementation of the `repeat` loop feature for the Chan language. The repeat loop allows you to execute a block of code a specific number of times.

## Syntax

The repeat loop syntax is:

```
repeat <count> times {
    // code to repeat
}
```

Where:
- `<count>` is an expression that evaluates to an integer
- `times` is a keyword
- The code inside the braces will be executed `<count>` times
-+
## Examples

### Basic repeat loop:

```
repeat 3 times {
    print("Hello, world!");
}
```

This will print "Hello, world!" three times.

### Nested repeat loops:

```
repeat 2 times {
    print("Outer loop");
    
    repeat 3 times {
        print("  Inner loop");
    }
}
```

This will print:
```
Outer loop
  Inner loop
  Inner loop
  Inner loop
Outer loop
  Inner loop
  Inner loop
  Inner loop
```

## Testing the Repeat Loop Feature

We've provided two ways to test the repeat loop feature:

### 1. Using the Simplified Interpreter

The `repeat_loop_interpreter.py` file contains a simplified version of the Chan interpreter that supports only the repeat loop and print statements.

Run it with:

```bash
python3 repeat_loop_interpreter.py simple_repeat_test.chan
```

### 2. Using the Original Interpreter

The implementation has also been added to the main Chan interpreter in the `use_case.py` file, which supports all language features.

Run it with:

```bash
python3 use_case.py run repeat_demo.chan
```

## Test Files

- `simple_repeat_test.chan`: A minimal test of the repeat loop feature with just print statements
- `repeat_test.chan`: A slightly more complex test of repeat loops
- `repeat_demo.chan`: A comprehensive demo of repeat loops with variables and other features

## Implementation Details

The repeat loop implementation consists of:

1. Lexer additions:
   - Added token types for 'repeat' and 'times' keywords

2. Parser additions:
   - Added a `repeat_loop` method to parse the repeat loop syntax
   - Updated the compound_statement method to handle repeat loops

3. Interpreter additions:
   - Added an evaluation handler for the 'repeat' node type
   - Implemented repeat loop execution logic

The implementation ensures that:
- The count expression is evaluated to an integer
- Negative counts are not allowed
- Nested repeat loops work correctly
- Return statements within a repeat loop exit the entire loop 