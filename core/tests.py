from django.test import TestCase



import time

def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

start_time = time.time()

print(fib(45))

end_time = time.time()
print(f"Time taken: {end_time - start_time:.2f} seconds")



