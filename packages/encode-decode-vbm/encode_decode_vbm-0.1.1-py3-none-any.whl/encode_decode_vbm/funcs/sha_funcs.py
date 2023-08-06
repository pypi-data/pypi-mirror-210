def translate(mess):
    bytes = [bin(i)[2:].zfill(8) for i in [ord(c) for c in mess]]
    bits = []
    for byte in bytes:
        for bit in byte:
            bits.append(int(bit))

    return bits


def fillZeros(bits, length=8, endian='LE'):
    l = len(bits)
    if endian == 'LE':
        for i in range(l, length):
            bits.append(0)
    else:
        while l < length:
            bits.insert(0, 0)
            l = len(bits)

    return bits


def b2tob16(val):
    val = ''.join([str(i) for i in val])
    binaries = []
    for d in range(0, len(val), 4):
        binaries.append('0b' + val[d:d+4])

    hexes = ''.join([hex(int(b, 2))[2:] for b in binaries])

    return hexes


def chunker(bits, chunk_length=8):
    chunked = [bits[b:b+chunk_length]
               for b in range(0, len(bits), chunk_length)]
    return chunked


def initializer(vals):
    binaries = [bin(int(v, 16))[2:] for v in vals]

    words = []
    for binary in binaries:
        word = []
        for b in binary:
            word.append(int(b))
        words.append(fillZeros(word, 32, 'BE'))

    return words


def preProcess(mess):
    bits = translate(mess)
    length = len(bits)
    mess_len = [int(b) for b in bin(length)[2:].zfill(64)]

    if length < 448:
        bits.append(1)
        bits = fillZeros(bits, 448, 'LE')
        bits += mess_len
        return [bits]
    elif 448 <= length <= 512:
        bits.append(1)
        bits = fillZeros(bits, 1024, 'LE')
        bits[-64:] = mess_len
        return chunker(bits, 512)
    else:
        bits.append(1)
        while (len(bits)+64) % 512 != 0:
            bits.append(0)
        bits += mess_len
        return chunker(bits, 512)


def isTrue(x): return x == 1


def if_(i, y, z): return y if isTrue(i) else z


def and_(i, j): return if_(i, j, 0)
def AND(i, j): return [and_(ia, ja) for ia, ja in zip(i, j)]


def not_(i): return if_(i, 0, 1)
def NOT(i): return [not_(x) for x in i]


def xor(i, j): return if_(i, not_(j), j)
def XOR(i, j): return [xor(ia, ja) for ia, ja in zip(i, j)]


def xorxor(i, j, l): return xor(i, xor(j, l))
def XORXOR(i, j, l): return [xorxor(ia, ja, la)
                             for ia, ja, la, in zip(i, j, l)]


def maj(i, j, k): return max([i, j,], key=[i, j, k].count)


def rotr(x, n): return x[-n:] + x[:-n]


def shr(x, n): return n * [0] + x[:-n]


def add(i, j):
    length = len(i)
    sums = list(range(length))
    c = 0

    for x in range(length-1, -1, -1):
        sums[x] = xorxor(i[x], j[x], c)
        c = maj(i[x], j[x], c)

    return sums
