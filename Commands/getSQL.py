import sqlite3
import math
import os

def makestate(list_, lv):
    if (list_ == None or len(list_) != 6):
        return []
    result = []
    if (lv >= 0):
        if (lv == 0):
            lv = 50
        import math
        rank = [[31,252,1.1],[31,252,1.0],[31,0,1.0],[0,0,0.9]]
        for j in range(4):
            single_res = []
            flg = 0
            for i in list_:
                if (flg == 0):
                    st = math.floor((i*2+rank[j][0]+rank[j][1]/4)*lv/100)+lv+10
                    flg = 1
                else:
                    st = math.floor((math.floor((i*2+rank[j][0]+rank[j][1]/4)*lv/100)+5)*rank[j][2])
                single_res.append(st)
            result.append(single_res)
    else:
        result = list_
    return result

def getstatus(type_, arg_, isreal):
    fpath = os.path.dirname(__file__)+'/sqldata/pokemon.sqlite3'
    poke_content = sqlite3.connect(fpath)
    c = poke_content.cursor()
    flg = 0
    txt = ''
    if (type_ == 'name'):
        txt = 'SELECT H,A,B,C,D,S FROM pokemon WHERE name = ? '
        flg = 1
    if (flg):
        # 全角カッコの許容
        arg = ''
        for i in range(len(arg_)):
            s = arg_[i]
            if (s == '（'):
                arg += '('
            elif (s == '）'):
                arg += ')'
            else:
                arg += s

        data = (arg,)
        c.execute(txt, data)
        list1 = c.fetchone()
        poke_content.commit()
        poke_content.close()
        return (list1 == None or len(list1) != 6), makestate(list1, isreal)
    poke_content.commit()
    poke_content.close()
    return -1, []
    
def sqlrequest(txt, tpl):
    fpath = os.path.dirname(__file__)+'/sqldata/pokemon.sqlite3'
    poke_content = sqlite3.connect(fpath)
    c = poke_content.cursor()
    list_ = list(tpl)
    #全角の許容
    for index, l in enumerate(list_):
        arg = ''
        for i in range(len(l)):
            s = l[i]
            if (s == '（'):
                arg += '('
            elif (s == '）'):
                arg += ')'
            else:
                arg += s
        list_[index] = arg

    tpl = list_
    try:
        c.execute(txt, tpl)
    except Exception as e:
        import traceback
        print('# traceback.format_exc()')
        t = traceback.format_exception_only(type(e), e)
        return t[0].rstrip('\n'), -2
    list1 = c.fetchone()
    if (list1 == None):
        return '', -1
    cnt = 0
    result = []
    sub = []
    for element in list1:
        sub.append(str(element))
    result.append(sub)
    for hit in c.fetchall():
        sub = []
        for element in hit:
            sub.append(str(element))
        result.append(sub)

    poke_content.commit()
    poke_content.close()
    return result, 1
    
def poke2num(name):
    fpath = os.path.dirname(__file__)+'/sqldata/pokemon.sqlite3'
    poke_content = sqlite3.connect(fpath)
    c = poke_content.cursor()
    txt = 'SELECT id FROM pokemon WHERE name = ?'
    arg = ''
    for i in range(len(name)):
        s = name[i]
        if (s == '（'):
            arg += '('
        elif (s == '）'):
            arg += ')'
        else:
            arg += s
    name = arg
    tpl = (name,)
    c.execute(txt, tpl)
    list1 = c.fetchone()
    if (list1 == None):
        return ''
    return list1[0]
    
def inname(name):
    fpath = os.path.dirname(__file__)+'/sqldata/pokemon.sqlite3'
    poke_content = sqlite3.connect(fpath)
    c = poke_content.cursor()
    txt = 'select name from pokemon where name like \'%\'||?||\'%\''
    arg = ''
    for i in range(len(name)):
        s = name[i]
        if (s == '（'):
            arg += '('
        elif (s == '）'):
            arg += ')'
        else:
            arg += s
    name = arg
    cnt = 0
    tpl = (name,)
    c.execute(txt, tpl)
    list1 = c.fetchone()
    if (list1 == None):
        return ['', -1]
    result = []
    cnt = 1
    for element in list1:
        result.append(str(element))
    for hit in c.fetchall():
        for element in hit:
            result.append(str(element))
            cnt += 1
    poke_content.commit()
    poke_content.close()
    return [result, cnt]

def getiv(poke, txt, lv, list_, check_h, rise=-1, down=-1):
    fpath = os.path.dirname(__file__)+'/sqldata/pokemon.sqlite3'
    poke_content = sqlite3.connect(fpath)
    c = poke_content.cursor()
    tpl = (poke,)
    c.execute(txt, tpl)
    list1 = c.fetchone()
    poke_content.commit()
    poke_content.close()

    if (list1 == None):
        return []

    nature = [1.0]*len(list_)
    if (rise != -1):
        nature[rise] = 1.1
    if (down != -1):
        nature[down] = 0.9
    ivlist = []
    for (i, n) in zip(range(len(list_)), nature):
        ivlist.append(makeiv(int(list1[i]), list_[i], int(lv), n,(i==check_h)))
    return ivlist

def makeiv(base, r_st, lv, nature, is_H):
    """実数値から取り得る個体値を計算"""
    if is_H:
        iv_min = math.ceil((r_st-lv-10)*(100/lv))-base*2
        iv_max = rdown_sub((r_st-lv-10+1)*(100/lv))-base*2
    else:
        iv_min = math.ceil((math.ceil(r_st/nature)-5)*(100/lv))-base*2
        iv_max = rdown_sub((math.ceil(r_st/nature)-5+1)*(100/lv))-base*2
    if (iv_max < 0 or iv_min > 31):
        return ['あほしね']
    else:
        if (iv_min < 0):
            iv_min = 0
        if (iv_max > 31):
            iv_max = 31
        if (iv_min == iv_max):
            return [iv_min]
        else:
            return [iv_min, iv_max]

def rdown_sub(num):
    """num が整数値なら-1、小数値なら切り捨て"""
    if num.is_integer():
        return (int(num) - 1)
    else:
        return int(num)

