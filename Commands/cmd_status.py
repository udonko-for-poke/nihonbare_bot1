import getSQL
import jaconv
import calc
import re

def st(arg1):        
    #引数にint型のものがあれば引数2とする
    isreal = -1
    if (len(arg1) <= 1):
        arg = arg1[0]
        arg2 = ''
    else:
        arg = arg1[0]
        arg2 = arg1[1]
    arg2_int =  int(re.sub(r'[^0-9].*', '', ('0'+arg2).replace(u'\xa0', '')))
    arg_int =  int(re.sub(r'[^0-9].*', '', ('0'+arg).replace(u'\xa0', '')))
    poke = arg
    if (arg == 'real' or arg2 == 'r'):
        isreal = 0
        poke = arg2
    elif (arg2 == 'real' or arg2 == 'r'):
        isreal = 0
        poke = arg
    elif (str(arg_int) == arg and 0 < arg_int and arg_int <= 100):
        isreal = arg_int
        poke = arg2
    elif (str(arg2_int) == arg2 and 0 < arg2_int and arg2_int <= 100):
        isreal = arg2_int
        poke = arg
    
    poke  = poke.replace('２', '2') #ポリゴン2の表記を統一
    poke  = jaconv.hira2kata(poke)  #平仮名をカタカナに
    #   数値を取得
    res, result = getSQL.getstatus('name', poke, isreal)
    if (not res):
        return 1, result
    else:
        result = getSQL.inname(poke)
        if (len(result) <= 0 or len(result) >= 10):
            return -1, poke
        else:
            return -2, result
    return

def korippo(poke):
    poke = jaconv.hira2kata(poke).replace('２', '2')
    cmd = 'select CAST(0.6*(H*2+31)+70 AS INT) from pokemon WHERE name = ?'
    tpl = (poke,)
    result = getSQL.sqlrequest(cmd, tpl)
    if (result[1]==-1):
        result = getSQL.inname(poke)
        if (len(result) <= 0 or len(result) >= 10):
            return -1, poke
        else:
            return -2, result

    HP = int(result[0])
    cmd = 'select get from pokemon WHERE name = ?'
    result = getSQL.sqlrequest(cmd, tpl)
    GET = int(result[0])
    B   = calc.get_B(HP, GET)
    if (B>=255):
        return 1, '∞'
    G = calc.get_G(B)
    value = (G/49806)**4
    return 1, str(round(value,2))

def calciv(poke, lv, args):
    st_list, check_list = [], []
    rise, down = -1, -1
    #引数の中に個体値チェックの箇所指定があるかどうかの確認
    for x in args:
        if (re.fullmatch(r'[0-9]*|[0-9]*(\+|-)', x)):
            if x[-1] == '+':
                x = x[:-1]
                rise = len(st_list)
            if x[-1] == '-':
                x = x[:-1]
                down = len(st_list)
            st_list.append(int(x))
        if (re.fullmatch(r'[A-DHS]*', x, flags=re.IGNORECASE)):
            for el in x:
                check_list.append(el.upper())

    if (not check_list):
        check_list = ['H', 'A', 'B', 'C', 'D', 'S']
    #求めたい個体値箇所と数値数が一致するかの確認
    if (len(st_list) != len(check_list)):
        return -3, None
    #個体値確認箇所にHPが含まれているかの確認
    else:
        if ('H' not in check_list):
            check_h = -1
        else:
            check_h = check_list.index('H')

        txt = 'SELECT ' +  ','.join(check_list) + ' FROM pokemon WHERE name = ?'
        result = getSQL.getiv(poke, txt, lv, st_list, check_h, rise, down)
        if (not result):
            return -1, poke
        else:
            return 1, result
    return