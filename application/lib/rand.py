
import random
import string

def randstring(N=6):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))

