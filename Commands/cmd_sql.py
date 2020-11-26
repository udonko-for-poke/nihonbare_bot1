import pickle
import os
import pickle
import re
import discord

async def sqlreq(message, cmd, argtpl):
    import getSQL
    print('SQL request->'+cmd+','+str(argtpl))
    result = await getSQL.sqlrequest(cmd, argtpl)
    print(result)
    if (result[1] == -1):
        await message.channel.send(f'{message.author.mention} 該当するデータが見つかりませんでした')
    elif (result[1] == -2):
        await message.channel.send(f'{message.author.mention} \n要求エラー：'+result[0])
    else:
        try:
            embed = discord.Embed(title="Result",description=result[0])
            await message.channel.send(f'{message.author.mention} ', embed=embed)
        except:
            await message.channel.send(f'{message.author.mention} エラー：該当するデータが多すぎます')
    return

async def addsql(ctx, arg, SQLCMD_PATH):
    if (len(arg) <= 1):
        await ctx.send(f'{ctx.author.mention} エラー：コマンドが短すぎます')
        return
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
        await ctx.send(f'{ctx.author.mention} エラー：コマンドが不適切です')
        return
        
    sql_dict = {}
    if os.path.getsize(SQLCMD_PATH) > 0:
        with open(SQLCMD_PATH, 'rb') as f:
            sql_dict = pickle.load(f)
                
        if (cmd in sql_dict):
            await ctx.send(f'{ctx.author.mention} エラー：既に定義されています')
            return
        
    sql_dict[cmd] = [text,'']
    with open(SQLCMD_PATH, 'wb') as f:
        pickle.dump(sql_dict, f)
    await ctx.send(f'{ctx.author.mention} コマンド「'+cmd+'」が登録されました')
    print('cmd='+cmd)
    print('text='+text)
    return

async def showsql(ctx, arg, SQLCMD_PATH):
    if os.path.getsize(SQLCMD_PATH) <= 0:
        await ctx.send(f'{ctx.author.mention} エラー：コマンドが登録されていません')
        return
    with open(SQLCMD_PATH, 'rb') as f:
        sql_dict = pickle.load(f)

    text = ''
    if (len(arg) == 0):
        for cmds in sql_dict:
            text += '\n　・' + cmds + '\n　' + sql_dict[cmds][1]
    else:
        for cmds in arg:
            if (cmds in sql_dict):
                text += '\n　・' + cmds + '\n　' + sql_dict[cmds][1]
            
    await ctx.send(f'{ctx.author.mention} '+text)
    return

async def delsql(ctx, cmd, SQLCMD_PATH):
    if os.path.getsize(SQLCMD_PATH) <= 0:
        await ctx.send(f'{ctx.author.mention} エラー：コマンドが登録されていません')
        return
    with open(SQLCMD_PATH, 'rb') as f:
        sql_dict = pickle.load(f)
    if (cmd in sql_dict):
        del sql_dict[cmd]
        with open(SQLCMD_PATH, 'wb') as f:
            pickle.dump(sql_dict, f)
        await ctx.send(f'{ctx.author.mention} 削除しました')
        return
    else:
        await ctx.send(f'{ctx.author.mention} エラー：コマンドが見つかりません')
    return

async def playsql(message, MY_SERVER, MY_SERVER2, FOR_BOT):
    if (message.channel.id != FOR_BOT and message.channel.guild.id != MY_SERVER and message.channel.guild.id != MY_SERVER2):
        return
    with message.channel.typing():
        mes = iter(message.content)
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
        await sqlreq(message, arg1, argtpl)
        return
            
async def editsql(message, SQLCMD_PATH):
    if os.path.getsize(SQLCMD_PATH) <= 0:
        await message.channel.send(f'{message.author.mention} エラー1：コマンドが見つかりません')
        return
    mes = iter(message.content)
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
        await message.channel.send(f'{message.author.mention} エラー2：コマンド「'+cmd+'」が見つかりません')
        return
        
    sql_dict[cmd][1] = text
    with open(SQLCMD_PATH, 'wb') as f:
        pickle.dump(sql_dict, f)
    await message.channel.send(f'{message.author.mention} 説明文を追加しました')

async def registered_sql(message, SQLCMD_PATH):
    if os.path.getsize(SQLCMD_PATH) <= 0:
        await message.channel.send(f'{message.author.mention} エラー1：コマンドが見つかりません')
        return

    mes = iter(message.content)
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
        await message.channel.send(f'{message.author.mention} エラー2：コマンド「'+cmd+'」が見つかりません')
        return
            
    await sqlreq(message, sql_dict[cmd][0] , tuple(arglist))
    return
