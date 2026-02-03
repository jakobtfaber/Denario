# filename: fibonacci.py
def calculate_fibonacci(n):
    fibonacci_numbers = [0, 1]
    for i in range(2, n):
        next_fib = fibonacci_numbers[i - 1] + fibonacci_numbers[i - 2]
        fibonacci_numbers.append(next_fib)
    return fibonacci_numbers

def main():
    num_fib = 0
    while num_fib <= 0:
        num_fib = int(input("Enter the number of Fibonacci numbers to display (greater than 0): "))
    fibonacci_sequence = calculate_fibonacci(num_fib)
    for number in fibonacci_sequence:
        print(number)
    for number in fibonacci_sequence:
        print('*' * number)

if __name__ == "__main__":
    main()