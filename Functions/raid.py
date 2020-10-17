import discord

# 在庫の確認
# 戻り値はポケモンの一覧(str), ポケモン数(int)
async def chk_stock(name, l_poke):
    send_txt = ''
    n = 0
    for poke in l_poke:
        if (name in poke):
            send_txt += '\n' + poke
            n += 1
            
    return send_txt, n

async def process_raid_add(ctx, arg, STOCK_PATH, l_poke):
    if (len(arg) <= 2):
        await ctx.send(f'{ctx.author.mention} ポケモン名が短すぎます。ポケモン名は3文字以上にしてください。')
        return

    print('add:' + arg)
    result = await chk_stock(arg, l_poke)
    if (result[1]):
        await ctx.send(f'{ctx.author.mention}'+result[0]+'\nのレイドが既に登録されています')
    else:
        l_poke.append(arg)
        with open(STOCK_PATH, 'w',encoding="utf-8_sig") as f:
            for x in l_poke:
                f.write(str(x) + "\n")
        await ctx.send(f'{ctx.author.mention}'+'\n' + str(arg) + 'レイドを登録しました')
    return

async def process_raid_check(ctx, arg, l_poke):
    if (len(arg) <= 2):
        await ctx.send(f'{ctx.author.mention} ポケモン名が短すぎます。ポケモン名は3文字以上にしてください。')
        return
    print('check:' + arg)
    result = await chk_stock(arg, l_poke)
    if (result[1]):
        await ctx.send(f'{ctx.author.mention}'+result[0]+'\nのレイドは開催済みです')
    else:
        await ctx.send(f'{ctx.author.mention}'+'\n' + str(arg) + 'レイドのデータはありません')
    return
