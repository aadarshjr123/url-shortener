import string

BASE62 = string.digits + string.ascii_letters

def encode_base62(num):
    if num == 0:
        return BASE62[0]
    
    result = []
    base = len(BASE62)

    while num >0:
        reminder = num % base
        result.append(BASE62[reminder])
        num //= base
    return ''.join(reversed(result))