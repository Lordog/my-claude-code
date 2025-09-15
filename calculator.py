def add(x, y):
    return x + y

def subtract(x, y):
    return x - y

def multiply(x, y):
    return x * y

def divide(x, y):
    if y == 0:
        return "Error: Cannot divide by zero"
    return x / y

def main():
    print("Simple Calculator")
    print("Operations: +, -, *, /")
    print("Type 'quit' to exit")
    
    while True:
        operation = input("\nEnter operation (+, -, *, /): ").strip()
        
        if operation.lower() == 'quit':
            break
            
        if operation not in ['+', '-', '*', '/']:
            print("Invalid operation. Please try again.")
            continue
            
        try:
            num1 = float(input("Enter first number: "))
            num2 = float(input("Enter second number: "))
        except ValueError:
            print("Invalid number. Please try again.")
            continue
            
        if operation == '+':
            result = add(num1, num2)
        elif operation == '-':
            result = subtract(num1, num2)
        elif operation == '*':
            result = multiply(num1, num2)
        elif operation == '/':
            result = divide(num1, num2)
            
        print(f"Result: {result}")

if __name__ == "__main__":
    main()