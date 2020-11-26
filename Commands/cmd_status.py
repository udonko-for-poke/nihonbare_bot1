import getSQL
import jaconv
import calc
import re

async def st(ctx, arg1):        
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
    #ポリゴン2の表記を統一
    poke  = poke.replace('２', '2')
    poke_ = jaconv.hira2kata(poke)
    print('status->'+poke+','+str(isreal))
    #   数値を取得
    result = await getSQL.getstatus('name', poke_, isreal)
    if (not result[0]):
        await ctx.send(f'{ctx.author.mention} \n'+result[1])
    else:
        result = await getSQL.getstatus('name', poke, isreal)
        if (not result[0]):
            await ctx.send(f'{ctx.author.mention} \n'+result[1])
        else:
            result = await getSQL.inname(poke_)
            if (result[1] == -1 or result[1] >= 10):
                await ctx.send(f'{ctx.author.mention} エラー：'+poke+'が見つかりませんでした')
            else:
                embed = discord.Embed(title="もしかして",description=result[0])
                await ctx.send(f'{ctx.author.mention} ', embed=embed)
    return

async def korippo(ctx, poke):
    poke = jaconv.hira2kata(poke).replace('２', '2')
    print('korippo->'+poke)
    cmd = 'select CAST(0.6*(H*2+31)+70 AS INT) from pokemon WHERE name = ?'
    tpl = (poke,)
    result = await getSQL.sqlrequest(cmd, tpl)
    if (result[1]==-1):
        result = await getSQL.inname(poke)
        if (result[1] == -1 or result[1] >= 10):
            await ctx.send(f'{ctx.author.mention} エラー：'+poke+'が見つかりませんでした')
        else:
            embed = discord.Embed(title="もしかして",description=result[0])
            await ctx.send(f'{ctx.author.mention} ', embed=embed)
        return
    HP = int(result[0])
    cmd = 'select get from pokemon WHERE name = ?'
    result = await getSQL.sqlrequest(cmd, tpl)
    GET = int(result[0])
    B   = calc.get_B(HP, GET)
    if (B>=255):
        await ctx.send(f'{ctx.author.mention} ∞(/コオリッポ)です')
        return
    G = calc.get_G(B)
    value = (G/49806)**4
    await ctx.send(f'{ctx.author.mention} '+str(round(value,2))+'(/コオリッポ)です')
    return

async def calciv(ctx, poke, lv, args):
    st_list, check_list = [], []
    ########################################　性格補正対応、及びインデントなし箇所指定への対応
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
    ########################################
    if (not check_list):
        check_list = ['H', 'A', 'B', 'C', 'D', 'S']
    #求めたい個体値箇所と数値数が一致するかの確認
    if (len(st_list) != len(check_list)):
        await ctx.send(f'{ctx.author.mention}エラー：引数の数が不正です')
    #個体値確認箇所にHPが含まれているかの確認
    else:
        if ('H' not in check_list):
            check_h = -1
        else:
            check_h = check_list.index('H')

        txt = 'SELECT ' +  ','.join(check_list) + ' FROM pokemon WHERE name = ?'
        ################################## 性格補正対応用の引数の追加
        result = await getSQL.getiv(poke, txt, lv, st_list, check_h, rise, down)
        ##############################################
        if (not result):
            await ctx.send(f'{ctx.author.mention} エラー：'+poke+'が見つかりませんでした')
        else:
            print('calciv:'+poke)
            await ctx.send(f'{ctx.author.mention}\n' + result)
    return