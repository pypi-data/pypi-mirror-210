import random
import string

# variables
upper_chars = string.ascii_uppercase
lower_chars = string.ascii_lowercase
number_chars = string.digits
special_chars = "-._~()'!*:@,;"

# generate
def generate(length=8, upper=True, lower=True, numbers=True, special=True):
    alphabet = ''

    if upper:
        alphabet += upper_chars
    if lower:
        alphabet += lower_chars
    if numbers:
        alphabet += number_chars
    if special:
        alphabet += special_chars
    
    if length == 8:
        password = ''.join(random.choice(alphabet) for i in range(8))
        return password
    else:
        password = ''.join(random.choice(alphabet) for i in range(length))
        return password