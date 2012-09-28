import unicodedata


def is_wide(c):
    return unicodedata.east_asian_width(c) in ['F', 'W', 'A']


def wlen(s):
    ret = len(s)
    for i in s:
        if is_wide(i):
            ret += 1
    return ret


def wwrap(s, maxc):
    ret = []
    while wlen(s) > maxc:
        # wlen(s) is at least maxc+1
        i = 0
        iz = 0
        while iz < maxc:
            if is_wide(s[i]):
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
