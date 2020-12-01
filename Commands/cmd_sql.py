import pickle
import os
import re
import getSQL

def sqlreq(cmd, argtpl):
    print('SQL request')
    result = getSQL.sqlrequest(cmd, argtpl)
    if (result[1] == -1):
        return False, '該当するデータが見つかりませんでした'
    elif (result[1] == -2):
        return False, '\n要求エラー：'+result[0]
    else:
        return 1, result[0]

def addsql(arg, SQLCMD_PATH):
    if (len(arg) <= 1):
        return -1, None     #不適切なコマンド
    cmd = arg[0]
    text = ''
    info=''
    flg = 0
    for i in range(len(arg)-1):
        text += arg[i+1] + ' '
        
    text_head = text[:6].lower()
    if (text_head == 'select'):
        pass
    else:
        return -1, None
        
    sql_dict = {}
    if os.path.getsize(SQLCMD_PATH) > 0:
        with open(SQLCMD_PATH, 'rb') as f:
            sql_dict = pickle.load(f)
                
        if (cmd in sql_dict):
            return -2, None     #定義済みのコマンド
        
    sql_dict[cmd] = [text,'']
    with open(SQLCMD_PATH, 'wb') as f:
        pickle.dump(sql_dict, f)
    return 1, cmd

def showsql(arg, SQLCMD_PATH):
    if os.path.getsize(SQLCMD_PATH) <= 0:
        return -3, None #コマンドが未登録
    with open(SQLCMD_PATH, 'rb') as f:
        sql_dict = pickle.load(f)

    text = []
    if (len(arg) == 0):
        for cmds in sql_dict:
            text.append(cmds)
        return 1, text
    else:
        for cmds in arg:
            if (cmds in sql_dict):
                text.append([cmds,sql_dict[cmds][1]])
        return 2, text

def delsql(cmd, SQLCMD_PATH):
    if os.path.getsize(SQLCMD_PATH) <= 0:
        return -3
    with open(SQLCMD_PATH, 'rb') as f:
        sql_dict = pickle.load(f)
    if (cmd in sql_dict):
        del sql_dict[cmd]
        with open(SQLCMD_PATH, 'wb') as f:
            pickle.dump(sql_dict, f)
        return 1
    return -4

def playsql(mes):
        arg1 = ''
        arg2 = ''
        flg = 0
        for i in mes:
            if (flg == 0):
                if(i=='\n'):
                    flg = 1
                else:
                    arg1 += i
            else:
                if(i=='\n'):
                    break
                arg2 += i
        arg1 = arg1[5:]
        arglist = arg2.split()
        argtpl  = tuple(arglist)
        return sqlreq(arg1, argtpl)
            
def editsql(mes, SQLCMD_PATH):
    if os.path.getsize(SQLCMD_PATH) <= 0:
        return 'エラー1：コマンドが見つかりません'
    cmd = ''
    text = ''
    flg = 0
    for i in mes:
        if (flg == 0):
            if(i=='\n'):
                flg = 1
            else:
                cmd += i
        else:
            text += i
                
    cmd = cmd[len('!editsql '):]
    sql_dict = {}
    with open(SQLCMD_PATH, 'rb') as f:
        sql_dict = pickle.load(f)
            
    if (cmd in sql_dict):
        pass
    else:
        return 'エラー2：コマンド「'+cmd+'」が見つかりません'
        
    sql_dict[cmd][1] = text
    with open(SQLCMD_PATH, 'wb') as f:
        pickle.dump(sql_dict, f)
    return '説明文を追加しました'

def registered_sql(mes, SQLCMD_PATH):
    if os.path.getsize(SQLCMD_PATH) <= 0:
        return False, 'エラー：コマンドが見つかりません'

    cmd = ''
    args = ''
    flg = 0
    for i in mes:
        if (flg == 0):
            if(i==' ' or i == '　'):
                flg = 1
            else:
                cmd += i
        else:
            args += i
    cmd = cmd[1:]
    arglist = re.split('[ 　]',args)
    if(len(arglist) == 1 and arglist[0] == ''):
        arglist = []
    with open(SQLCMD_PATH, 'rb') as f:
        sql_dict = pickle.load(f)
        
    if (cmd in sql_dict):
        pass
    else:
        return False, 'エラー：コマンド「'+cmd+'」が見つかりません'
            
    return sqlreq(sql_dict[cmd][0] , tuple(arglist))
