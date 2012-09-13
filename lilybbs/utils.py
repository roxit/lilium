

def is_zh(c):
    # TODO
    return any([u'\u4E00' <= c <= u'\u62FF',
            u'\u6300' <= c <= u'\u77FF',
            u'\u7800' <= c <= u'\u8CFF',
            u'\u8D00' <= c <= u'\u9FCC',
            u'\uFF00' <= c <= u'\uFFEF',
            u'\u3001' <= c <= u'\u303F'])    # TODO


def len_zh(s):
    ret = len(s)
    for i in s:
        if is_zh(i):
            ret += 1
    return ret


def wrap_zh(s, maxc):
    ret = []
    while len_zh(s) > maxc:
        # len_zh(s) is at least maxc+1
        i = 0
        iz = 0
        while iz < maxc:
            if is_zh(s[i]):
                iz += 2
            else:
                iz += 1
            i += 1
        # iz == maxc or iz == max+1,
        # i might be greater than len(s),
        # but it's okay for slicing
        ret.append(s[:i])
        s = s[i:]
    if s:
        ret.append(s)
    return ret

