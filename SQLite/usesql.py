import sqlite3

def poke_insert(name, datas, cur, id_):
    type1 = datas[0][0]
    type2 = datas[0][1]
    H = datas[1][0]
    A = datas[1][1]
    B = datas[1][2]
    C = datas[1][3]
    D = datas[1][4]
    S = datas[1][5]
    exp=datas[2]
    ability1=datas[3][0]
    ability2=datas[3][1]
    ability3=datas[3][2]
    evo     =datas[4]
    is8     =int(datas[5]!=0)
    get     =datas[6]
    value = (id_,name,type1,type2,H,A,B,C,D,S,get,exp,ability1,ability2,ability3,evo,is8)
    print(value)
    cur.execute('INSERT INTO pokemon(ID, name, type1, type2, H, A, B, C, D, S, get, exp, ability1, ability2, ability3, evo, is8) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',value)
    return
    
def type_insert(data, c):
    value = (data[0], data[1], data[2])
    c.execute('INSERT INTO Type(ID, name, name2) values (?, ?, ?)', value)
    return
    
def ability_insert(id_,name, text, c):
    value = (id_, name, text)
    c.execute('INSERT INTO Ability(ID, name, text) values (?, ?, ?)', value)
    return

def move_insert(value, c):
    c.execute('INSERT INTO Move(ID, name, type, power, accuracy, pp, class, direct, text, target, protect, kana) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', value)
    return
    
def poke2move_insert(name, data, c):
    value = (name, data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8])
    c.execute('INSERT INTO poke2move(pokemon, move, lv, machine, record, egg, teach, old, special, before) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', value)
    return
