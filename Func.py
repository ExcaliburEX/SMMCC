from alive_progress import alive_bar
from math import sqrt

def Prime(n):
    if n == 1:
        return False
    for num in range(2, int(sqrt(n))+1):
        if n % num == 0:
            return False
    else:
        return True
    

def test(rng, m, pos, window):
    sum_prime = 0
    # with alive_bar(rng // m) as bar:
    for i in range(rng // m * (pos-1), rng // m * (pos)):
        # bar()
        window['progressbar-%d'%(pos)].update_bar(100/(rng//m) * (i-(rng // m * (pos-1))) + 1)
        if Prime(i):
            sum_prime += 1
    return sum_prime


