# ToyLang Features and Tokens Documentation

Based on the provided test case (`aiscream.chan`), here's a comprehensive documentation of the language features and tokens available in the ToyLang interpreter:

## Variables and Constants
- **Variable Declaration**: `let x = 5;`
- **Constant Declaration**: `const y = 10;`
- **Assignment**: `counter = counter + 1;`

## Data Types
1. **Numbers**: 
   - Integers: `5`, `10`, `3`
   - Expressions: `counter + 1`, `parseInt(age) + 5`

2. **Strings**:
   - String literals: `"Hello, Chan!"`, `"x is less than y"`
   - String concatenation: `"Hello, " + name`

3. **Booleans**:
   - Boolean expressions: `x > y` (evaluates to `true` or `false`)
   - Boolean literals: `true` in `let mixed = [1, "hello", true];`

4. **Arrays**:
   - Array declaration: `let numbers = [1, 2, 3, 4, 5];`
   - Mixed type arrays: `let mixed = [1, "hello", true];`
   - Array indexing: `numbers[2]`
   - Array modification: `numbers[0] = 10;`

5. **Null**: (Though not shown in the test case, it's supported)

## Operators
1. **Arithmetic**:
   - Addition: `+` 
   - Multiplication: `*`
   - (Subtraction and division are also supported)

2. **Comparison**:
   - Less than: `<`
   - Greater than: `>`
   - (Equal to `==`, not equal to `!=`, greater than or equal to `>=`, less than or equal to `<=` are also supported)

3. **Logical**:
   - AND: `and`
   - OR: `or`
   - NOT: `not`
   - (Though not shown explicitly in the test case)

## Control Structures
1. **Conditional**:
   ```
   if (x < y) {
       print("x is less than y");
   } else {
       print("x is greater than or equal to y");
   }
   ```

2. **Loops**:
   - While loop:
     ```
     while (counter < 3) {
         print(counter);
         counter = counter + 1;
     }
     ```
   - Repeat loop:
     ```
     repeat 3 times {
         print("Hello, world!");
     }
     ```
   - Repeat with variables and expressions:
     ```
     repeat iterations times { ... }
     repeat iterations - 2 times { ... }
     ```
   - Nested repeat loops

## Functions
1. **Function Definition**:
   ```
   def greet() {
       print("Hello");
   }
   ```

2. **Function Calls**:
   - Direct calls: `person1.greet();`
   - With arguments: `add(2, 3);`

3. **Arrow Functions**:
   - Multi-parameter: `let add = (x, y) => x + y;`
   - Single parameter: `let square = x => x * x;`

## Data Structures
1. **Structs**:
   ```
   struct Point {
       x, y
   }
   ```
   - Creation: `const p = Point(5, 10);`
   - Field access: `p.x`

2. **Classes**:
   ```
   class Person {
       def greet() {
           print("Hello");
       }
   }
   ```
   - Instantiation: `let person1 = new Person();`
   - Method calls: `person1.greet();`

## Input/Output
1. **Output**:
   - `print(sum);`
   - `print("Hello, " + name);`

2. **Input**:
   - With prompt: `let name = input("Enter your name: ");`
   - Number conversion: `parseInt(age)`

## Comments
- Single-line comments: `// Arrow function example`

## Special Tokens
- **Keywords**: `let`, `const`, `if`, `else`, `while`, `print`, `struct`, `class`, `def`, `new`, `repeat`, `times`, `input`, `parseInt`
- **Punctuation**: `{}`, `()`, `[]`, `;`, `,`, `.`, `=`, `=>`, `+`, `*`, `<`, `>`
- **New/Repeat Feature**: The `repeat ... times { ... }` construct for simple iteration

## Code Blocks
- Defined using curly braces: `{ ... }`
- Used in control structures, function definitions, and class declarations

## Identifier Rules
- Can include letters, numbers, and underscores
- First character must be a letter or underscore
- Examples: `x`, `y`, `sum`, `greeting`, `is_greater`, `counter`, `Point`, `Person`, `add`, `multiply`, `square`, `numbers`, `mixed`, `name`, `age`, `iterations`, `index`

This documentation covers all the language features and tokens demonstrated in the provided test case. The ToyLang language combines familiar syntax from JavaScript, Python, and other popular languages into a clean, easy-to-use scripting language with modern features. 