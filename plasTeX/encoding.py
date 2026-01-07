import string

def stringletters():
    return string.ascii_letters

def numToRoman(x: int) -> str:
    """ Represent the given positive integer in roman numerals. """

    numerals = [
        (1000, "M"),
        (900, "CM"),
        (500, "D"),
        (400, "CD"),
        (100, "C"),
        (90, "XC"),
        (50, "L"),
        (40, "XL"),
        (10, "X"),
        (9, "IX"),
        (5, "V"),
        (4, "IV"),
        (1, "I"),
    ]

    s = ""
    for n, t in numerals:
        k, r = divmod(x, n)
        s += t*k
        x -= n*k

    return s

def numToAlpha(i):
    """ Represent the given positive integer in letters.
        e.g. 1 → 'a'
             26 → 'aa'
             27 → 'ab'
    """

    i -= 1

    l = 26
    alphabet = string.ascii_letters[:l]
    digits = 1
    
    while i >= l**digits:
        i -= l**digits
        digits += 1

    s = ''

    for n in range(digits):
        r = i % l
        s = alphabet[r] + s
        i = (i - r) // l

    return s
