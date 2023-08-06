
def preproc(mess):
    bytes = [bin(i)[2:].zfill(8) for i in [ord(c) for c in mess]]
    bits = []
    for byte in bytes:
        for bit in byte:
            bits.append(int(bit))

    length = len(bits)

    num = length-(length//40*40)

    while (len(bits) % 40) != 0:
        bits.append(0)

    return (bits, num)


def base32e(mess):
    dict = {
        0: 'A', 1: 'B', 2: 'C', 3: 'D',
        4: 'E', 5: 'F', 6: 'G', 7: 'H',
        8: 'I', 9: 'J', 10: 'K', 11: 'L',
        12: 'M', 13: 'N', 14: 'O', 15: 'P',
        16: 'Q', 17: 'R', 18: 'S', 19: 'T',
        20: 'U', 21: 'V', 22: 'W', 23: 'X',
        24: 'Y', 25: 'Z', 26: '2', 27: '3',
        28: '4', 29: '5', 30: '6', 31: '7'
    }

    mess, num = preproc(mess)
    mess = [str(i) for i in mess]
    mess = [''.join(mess[i:i+5]) for i in range(0, len(mess), 5)]
    mess = [dict[int('0b'+i, 2)] for i in mess]

    if num == 8:
        mess[-6:] = ['=', '=', '=', '=', '=', '=']
    elif num == 16:
        mess[-4:] = ['=', '=', '=', '=']
    elif num == 24:
        mess[-3:] = ['=', '=', '=']
    elif num == 32:
        mess[-1:] = '='

    mess = ''.join(mess)

    return mess


def base32d(mess):
    dict = {'A': '00000', 'B': '00001', 'C': '00010', 'D': '00011',
            'E': '00100', 'F': '00101', 'G': '00110', 'H': '00111',
            'I': '01000', 'J': '01001', 'K': '01010', 'L': '01011',
            'M': '01100', 'N': '01101', 'O': '01110', 'P': '01111',
            'Q': '10000', 'R': '10001', 'S': '10010', 'T': '10011',
            'U': '10100', 'V': '10101', 'W': '10110', 'X': '10111',
            'Y': '11000', 'Z': '11001', '2': '11010', '3': '11011',
            '4': '11100', '5': '11101', '6': '11110', '7': '11111'}

    mess = [str(char) for char in mess]
    c = mess.count('=')
    mess = mess[:-c] if c != 0 else mess

    num = 0
    if c == 6:
        num = 8
    elif c == 4:
        num = 16
    elif c == 3:
        num = 24
    elif c == 1:
        num = 32

    length = ((len(mess)*5)//40*40)+num

    mess = [dict[i] for i in mess]
    mess = ''.join(mess)
    mess = ''.join([chr(int('0b' + mess[i:i+8], 2))
                   for i in range(0, length, 8)])

    return mess
