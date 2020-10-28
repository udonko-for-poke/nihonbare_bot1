import requests
import sys
import os
from bs4 import BeautifulSoup
from sys import exit
import re
import asyncio
import sqlite3
import usesql
import time

def make_table():
    poke_content = sqlite3.connect(os.path.dirname(__file__)+'/sqldata/pokemon.sqlite3')
    poke_c = poke_content.cursor()
    poke_c.execute('create table pokemon(ID text PRIMARY KEY, name text, type1 int, type2 int, H int, A int, B int, C int, D int, S int, get int, exp int, ability1 int, ability2 int, ability3 int, evo int)')    
    poke_content.commit()
    poke_content.close()
    return

def get_move_elements(e, target, text, c):
    m1 = re.search(r'/search/\?move=[0-9]*"', str(e[0]))
    m2 = re.search(r'data-sort-value=".*?"', str(e[0]))
    id_ = int(m1.group()[len('/search/?move='):-1])
    name = e[0].get_text()
#    print(m2)
#    print(str(e[0]))
    kana = m2.group()[len('data-sort-value="'):-1]
    
    m1 = re.search(r'type=[0-9]*"', str(e[1]))
    type_ = int(m1.group()[len('type='):-1])
    class__ = e[2].get_text()
    power   = int(re.sub(r'[^0-9].*', '', ('0'+e[3].get_text()).replace(u'\xa0', '')))
    accuracy= int(re.sub(r'[^0-9].*', '', ('0'+e[5].get_text()).replace(u'\xa0', '')))
    pp      = int(re.sub(r'[^0-9].*', '', ('0'+e[6].get_text()).replace(u'\xa0', '')))
    if(e[7].get_text() == '直○'):
        direct = 1
    else:
        direct = 0
    if(e[8].get_text() == '守○'):
        protect = 1
    else:
        protect = 0

    print(name)
    value = (id_, name, type_, power, accuracy, pp, class__, direct, text, target, protect, kana)
    usesql.move_insert(value, c)
    return

def get_pokedata(urlName):
    type_  = ['']*2
    status = [0]*6
    ability = [-1]*3
    evo = 0
    is8 = -1
    i = 0

    url     = requests.get(urlName)
    soup1   = BeautifulSoup(url.content, 'html.parser')
    elems1  = soup1.find(class_ = 'table layout_left')
    elems0  = soup1.find(class_ = 'select_list gen_list')

    #後で使うsoupの作成
    
    headsoup= BeautifulSoup(str(elems0).encode(), 'html.parser')
    soup2   = BeautifulSoup(str(elems1).encode(), 'html.parser')
    imgselem= soup2.find(class_ = 'type')
    imgssoup= BeautifulSoup(str(imgselem).encode(), 'html.parser')
    elems2  = soup1.find(class_ = 'table layout_right')
    rsoup   = BeautifulSoup(str(elems2).encode(), 'html.parser')
    del(elems1)
    del(elems2)
    del(imgselem)
    
    #is8
    is8_ = headsoup.find_all(class_ = 'menu_icon menu_icon_mini soft_ss')

    name = soup2.find(class_ = 'head').get_text()
    #タイプはタイプIDを画像のリンクから得る
    type_elems= imgssoup.find_all('img')
    for imgdata in type_elems:
        type__ = imgdata.get('src').replace('.gif', '')
        type_[i] = int(re.sub(r'.*n', '', type__))
        i += 1
    #進化状態は進化の流れから正規表現を使って判定する
    evotxt    = soup2.find(class_ = 'evo_list')
    if (evotxt == None):
        evo = -1
    else:
        m1 = re.search(r'『'+name+'』から進化', evotxt.get_text())
        m2 = re.search(r'↓'+name+'⇒.*から進化', evotxt.get_text())
        if (m1 != None and m2 != None):
            evo = 2
        elif (m2 != None):
            evo = 1
        else:
            evo = 0
    
    status_ = rsoup.find_all(class_ = 'left')
    for i in range(6):
        status[i] = int(re.sub(r'[^0-9].*', '', status_[i+1].get_text().replace(u'\xa0', '')))
        
    get = int(re.sub(r'[^0-9].*', '', status_[17].get_text().replace(u'\xa0', '')))

    exptxt = status_[20].get_text()
    exp_ = ''
    for i in exptxt:
        if ('9'<i or '0'>i):
            break
        else:
            exp_ += i
    
    #特性は特性idをリンクから得る
    abilitys = rsoup.find_all('a')
    i = 0
    for ab in abilitys:
        #正規表現でタグを除去
        m1 = re.search(r'<.*tokusei=.*">.*</a>', str(ab))
        if (m1 != None):
            abtext = re.sub(r'<.*tokusei=|">.*</a>', '', str(ab))
            if (ab.get_text()[0]!='*'):
                ability[i] = int(abtext)
                i += 1
            else:
                ability[2] = int(abtext)
                
            
    return type_, status, int(exp_), ability, evo, len(is8_), get

def move_check(data, move):
    flg = 0
    i = 0
    for d in data:
        if d[0] == move:
            flg = 1
            break
        else:
            i += 1
            
    if (flg):
        return i
    return -1

def get_pokedata2(mainurl):
    flg = 0
    moves   = []
    url     = requests.get(mainurl)
    soup1   = BeautifulSoup(url.content, 'html.parser')
    elems1  = soup1.select('#move_list')
    
    soup2   = BeautifulSoup(str(elems1), 'html.parser')
    elems2  = soup2.find_all('tr')
    
    for elem in elems2:
        if ("class=\"move_head\"" in str(elem)):
            atr = elem.get("id")
            if (atr == 'level_move'):
                flg = 1
            elif (atr == 'machine_move'):
                flg = 2
            elif (atr == 'record_move'):
                flg = 3
            elif (atr == 'egg_move'):
                flg = 4
            elif (atr == 'tutors_move'):
                flg = 5
            elif ('id="past_move"' in str(elem)):
                flg = 6
            elif (atr == 'sp_move' or atr == 'present_move'):
                flg = 7
            else:
                print(atr)
        elif ('id="past_move"' in str(elem)):
            flg = 6
            continue
        elif ('id="pre_move"' in str(elem)):
            flg = 8
            continue
        elif ('id="present_move"' in str(elem)):
            flg = 7
            continue
        elif ("class=\"move_head2\"" in str(elem) or 'class="move_condition_row"' in str(elem) or 'class="move_detail_row' in str(elem) or '過去作でしか覚えられない技<' in str(elem)):
            continue
        elif (elem.get_text() == 'なし' or 'の時だけ覚える技' in str(elem) or ("class=\"move_note\"" in str(elem)) or '配布限定の特別な技' in str(elem)):
            continue
        else:
#            print(flg)
            m1 = re.search(r'/search/\?move=[0-9]*"', str(elem))
#            print(elem)
            id_ = int(m1.group()[len('/search/?move='):-1])
            if (flg == 1):
                m2 = re.search(r'<span class="value">.*?</span>', str(elem))
                if (m2 == None):
                    lv = 0
                else:
                    lv = int('0'+m2.group()[len('<span class="value">'):-7])
#                    print(lv)
            else:
                lv = 1
            chk = move_check(moves, id_)
            if (chk == -1):
                addarr = [id_, -1, 0, 0, 0, 0, 0, 0, 0]
                addarr[flg] = lv
                moves.append(addarr)
            else:
                moves[chk][flg] = lv
            
    return moves



def main():
    allpokeurl = "https://yakkun.com/swsh/zukan/#mode=0,filter=0,sort=no"
    pokeurl = 'https://yakkun.com/swsh'
    url     = requests.get(allpokeurl)
    pokesoup= BeautifulSoup(url.content, 'html.parser')
    elems0  = pokesoup.find(class_ = 'pokemon_list')
#    print(elems0.get_text())
#    return
    pokelistsoup = BeautifulSoup(str(elems0).encode(), 'html.parser')
    del(url)
    pokes   = pokelistsoup.find_all('a')
    pokeid = 0
    poke_content = sqlite3.connect(os.path.dirname(__file__)+'/sqldata/pokemon.sqlite3')
    poke_c = poke_content.cursor()
    poke_c.execute('drop table pokemon')
    poke_c.execute('create table pokemon(ID TEXT PRIMARY KEY, name TEXT, type1 INTEGER, type2 INTEGER, H INTEGER, A INTEGER, B INTEGER, C INTEGER, D INTEGER, S INTEGER, get INTEGER, exp INTEGER, ability1 INTEGER, ability2 INTEGER, ability3 INTEGER, evo INTEGER, is8 INTEGER)')
    for pokelink in pokes:
#        pokeid += 1
#        if (pokeid != 421):
#            continue
        pokename = pokelink.get_text()
        m1 = re.search(r'/zukan/n[0-9]*.*?"', str(pokelink))
#        print(str(m1.group())[:-1])
        result1 = get_pokedata(pokeurl+str(m1.group())[:-1])
#        print(result1)
        usesql.poke_insert(pokename, result1, poke_c, str(m1.group()).replace('/zukan/n', '')[:-1])
#        print(pokename)
        time.sleep(0.1)

    poke_content.commit()
    poke_content.close()
        
    return(1)
            
def make_type():
    l = []
    l.append((0, 'ノーマル', '無'))
    l.append((1, 'かくとう', '闘'))
    l.append((2, 'ひこう', '飛'))
    l.append((3, 'どく', '毒'))
    l.append((4, 'じめん', '地'))
    l.append((5, 'いわ', '岩'))
    l.append((6, 'むし', '虫'))
    l.append((7, 'ゴースト', '霊'))
    l.append((8, 'はがね', '鋼'))
    l.append((9, 'ほのお', '炎'))
    l.append((10, 'みず', '水'))
    l.append((11,'くさ','草'))
    l.append((12, 'でんき', '電'))
    l.append((13, 'エスパー', '超'))
    l.append((14, 'こおり', '氷'))
    l.append((15, 'ドラゴン', '竜'))
    l.append((16, 'あく', '悪'))
    l.append((17, 'フェアリー', '妖'))
    poke_content = sqlite3.connect(os.path.dirname(__file__)+'/sqldata/pokemon.sqlite3')
    poke_c = poke_content.cursor()
    poke_c.execute('create table Type(ID int PRIMARY KEY, name TEXT, name2 TEXT)')
    for i in l:
        usesql.type_insert(i, poke_c)
    poke_content.commit()
    poke_content.close()
    return
    
def make_ability():
    mainurl = 'https://yakkun.com/swsh/ability_list.htm'
    url     = requests.get(mainurl)
    soup    = BeautifulSoup(url.content, 'html.parser')
    elems   = soup.find_all('td')
    id_ = ''
    name = ''

    poke_content = sqlite3.connect(os.path.dirname(__file__)+'/sqldata/pokemon.sqlite3')
    poke_c = poke_content.cursor()
    poke_c.execute('drop table Ability')
    poke_c.execute('create table Ability(ID int PRIMARY KEY, name TEXT, text TEXT)')

    for i in range(len(elems)):
        if (i%2):
            text = elems[i].get_text().replace(u'\xa0', '')
            print('name='+name)
            usesql.ability_insert(int(id_), name, text, poke_c)
        else:
            elem = str(elems[i])
            m1 = re.search(r'/search/\?tokusei=[0-9]*"', elem)
            id_  = m1.group()[len('/search/?tokusei='):-1]
            name = elems[i].get_text().replace(u'\xa0', '')
            
    poke_content.commit()
    poke_content.close()
    return

def make_move():
    mainurl = 'https://yakkun.com/swsh/move_list.htm'
    url     = requests.get(mainurl)
    soup    = BeautifulSoup(url.content, 'html.parser')
    elems1   = soup.find_all(class_ = 'sort_tr')
    elems2   = soup.find_all(class_ = 'sort_tr_next')
    target = []
    text   = []

    poke_content = sqlite3.connect(os.path.dirname(__file__)+'/sqldata/pokemon.sqlite3')
    poke_c = poke_content.cursor()
    poke_c.execute('drop table Move')
    poke_c.execute('create table Move(ID INTEGER PRIMARY KEY, name TEXT, type INTEGER, power INTEGER, accuracy INTEGER, pp INTEGER, class INTEGER, direct INTEGER, text TEXT, target TEXT, protect INTEGER, kana TEXT)')
    

    for elem in elems2:
        nextsoup = BeautifulSoup(str(elem).encode(), 'html.parser')
        e        = nextsoup.find_all('td')
        target.append(e[0].get_text())
        text.append(e[1].get_text())
    del(elems2)
    
    i = 0
    for elem in elems1:
        nextsoup = BeautifulSoup(str(elem).encode(), 'html.parser')
        e        = nextsoup.find_all('td')
        get_move_elements(e, target[i], text[i], poke_c)
        i += 1
        
    poke_content.commit()
    poke_content.close()

    return

def make_poke2move():
    allpokeurl = "https://yakkun.com/swsh/zukan/#mode=0,filter=0,sort=no"
    pokeurl = 'https://yakkun.com/swsh'
    url     = requests.get(allpokeurl)
    pokesoup= BeautifulSoup(url.content, 'html.parser')
    elems0  = pokesoup.find(class_ = 'pokemon_list')
#    print(elems0.get_text())
    pokelistsoup = BeautifulSoup(str(elems0).encode(), 'html.parser')
    del(url)
    pokes   = pokelistsoup.find_all('a')

    poke_content = sqlite3.connect(os.path.dirname(__file__)+'/sqldata/pokemon.sqlite3')
    poke_c = poke_content.cursor()
    poke_c.execute('drop table poke2move')
    poke_c.execute('create table poke2move(pokemon TEXT, move INT, lv INT, machine INT, record INT, egg INT, teach INT, old INT, special INT, before, PRIMARY KEY(pokemon, move))')
    for pokelink in pokes:
        pokename = pokelink.get_text()
        m1 = re.search(r'/zukan/n[0-9]*.*?"', str(pokelink))
        name = str(m1.group()).replace('/zukan/n', '')[:-1]
        print(name)
        result1 = get_pokedata2(pokeurl+str(m1.group())[:-1])#, str(m1.group()).replace('/zukan/n', '')[:-1])
        for data in result1:
            usesql.poke2move_insert(name, data, poke_c)
        time.sleep(0.1)

    poke_content.commit()
    poke_content.close()
    


if __name__ == '__main__':
#    make_table()
#    make_type()
    make_ability()
    make_move()
#    print(get_pokedata2('https://yakkun.com/swsh/zukan/n96'))
    make_poke2move()
    main()
#    result1 = get_pokedata('https://yakkun.com/swsh/zukan/n129')
#    print(result1)
#    print('type   ='+str(result1[0]))
#    print('status ='+str(result1[1]))
#    print('exp    ='+str(result1[2]))
#    print('ability='+str(result1[3]))
#    print('evo    ='+str(result1[4]))
#    print('is8    ='+str(result1[5]))
    exit(0)
    