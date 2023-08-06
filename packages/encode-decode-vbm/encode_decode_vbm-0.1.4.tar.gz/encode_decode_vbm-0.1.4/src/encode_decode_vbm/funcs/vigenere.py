def tonum(mess):

    dict = {'a': 0, 'b': 1,
            'c': 2, 'd': 3,
            'e': 4, 'f': 5,
            'g': 6, 'h': 7,
            'i': 8, 'j': 9,
            'k': 10, 'l': 11,
            'm': 12, 'n': 13,
            'o': 14, 'p': 15,
            'q': 16, 'r': 17,
            's': 18, 't': 19,
            'u': 20, 'v': 21,
            'w': 22, 'x': 23,
            'y': 24, 'z': 25}

    mess = [char.lower() for char in mess]

    mess = [dict[i] if i in dict.keys() else i for i in mess]

    mess1 = [i for i in mess if i in dict.values()]

    m = {}

    for i in range(len(mess)):
        if type(mess[i]) != int:
            m[i] = mess[i]

    mess_l = len(mess1)

    return mess, m, mess1, mess_l


def keytolist(key, mess_l: int):

    whole = mess_l//len(key)
    partial = mess_l-(len(key)*whole)

    key_part = key[:partial]

    key = key*whole+key_part

    key = tonum(key)[0]

    return key


dict = {0: 'a', 1: 'b',
        2: 'c', 3: 'd',
        4: 'e', 5: 'f',
        6: 'g', 7: 'h',
        8: 'i', 9: 'j',
        10: 'k', 11: 'l',
        12: 'm', 13: 'n',
        14: 'o', 15: 'p',
        16: 'q', 17: 'r',
        18: 's', 19: 't',
        20: 'u', 21: 'v',
        22: 'w', 23: 'x',
        24: 'y', 25: 'z'}


def cypher(mess, key):

    global dict

    mess, m, mess1, mess_l = tonum(mess)

    key = keytolist(key, mess_l)

    cypher = [dict[(key[i] + mess1[i]) % 26] for i in range(len(mess1))]

    for i in m:
        cypher.insert(i, m[i])

    cypher = ''.join(cypher)

    return cypher


def decypher(mess, key):

    global dict

    mess, m, mess1, mess_l = tonum(mess)
    key = keytolist(key, mess_l)

    decypher = [dict[(mess1[i] - key[i]) % 26] for i in range(len(mess1))]

    for i in m:
        decypher.insert(i, m[i])

    decypher = ''.join(decypher)

    return decypher
