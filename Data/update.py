import pickle

with open('cmdsql.pickle', 'rb') as f:
    sql_dict = pickle.load(f)

newdata = {}

def getargc(text):
    i = 0
    for c in text:
        if (c == '?'):
            i += 1
    return i

for cmd in sql_dict.keys():
    text = sql_dict[cmd][0]
    info = sql_dict[cmd][1]
    argc = getargc(text)
    newdata[cmd] = {'SQL':text, 'info':info, 'argc':argc}

with open('cmdsql.pickle', 'wb') as f:
    pickle.dump(newdata, f)