def isprime(number):
    for x in range (2,int(number**0.5)+1):
        if number % x ==0:
            return False
    return True