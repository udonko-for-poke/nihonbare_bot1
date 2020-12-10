def lookup_ev(id_name, _list):
    for i, x in enumerate(_list):
        if id_name in x:
            return i
    else:
        return -1