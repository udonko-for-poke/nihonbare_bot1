# 在庫の確認
# 戻り値はポケモンの一覧(str), ポケモン数(int)
def chk_stock(name, l_poke):
    send_txt = ''
    n = 0
    for poke in l_poke:
        if (name in poke):
            send_txt += '\n' + poke
            n += 1
            
    return send_txt, n

#レイドの登録
async def process_raid_add(ctx, arg, STOCK_PATH, l_poke):
    if (len(arg) <= 2):
        await ctx.send(f'{ctx.author.mention} ポケモン名が短すぎます。ポケモン名は3文字以上にしてください。')
        return

    print('add:' + arg)
    result = chk_stock(arg, l_poke)
    if (result[1]):
        await ctx.send(f'{ctx.author.mention}'+result[0]+'\nのレイドが既に登録されています')
    else:
        l_poke.append(arg)
        with open(STOCK_PATH, 'w',encoding="utf-8_sig") as f:
            for x in l_poke:
                f.write(str(x) + "\n")
        await ctx.send(f'{ctx.author.mention}'+'\n' + str(arg) + 'レイドを登録しました')
    return l_poke

#在庫確認
async def process_raid_check(ctx, arg, l_poke):
    if (len(arg) <= 2):
        await ctx.send(f'{ctx.author.mention} ポケモン名が短すぎます。ポケモン名は3文字以上にしてください。')
        return
    print('check:' + arg)
    result = chk_stock(arg, l_poke)
    if (result[1]):
        await ctx.send(f'{ctx.author.mention}'+result[0]+'\nのレイドは開催済みです')
    else:
        await ctx.send(f'{ctx.author.mention}'+'\n' + str(arg) + 'レイドのデータはありません')
    return


async def process_raid_del(ctx, name, STOCK_PATH, l_poke):
    if (ctx.message.author.top_role.id != HOST_ROLE):
        await ctx.send(f'{ctx.author.mention} 権限が足りません')
        return
    print('del:' + name)
    if (name in l_poke):
        l_poke.remove(name)
        with open(STOCK_PATH, 'w',encoding="utf-8_sig") as f:
            for x in l_poke:
                f.write(str(x) + "\n")
        await ctx.send(f'{ctx.author.mention}'+'\n' + str(name) + 'レイドを削除しました')
    else:
        await ctx.send(f'{ctx.author.mention}'+'\n' + str(name) + 'レイドが見つかりませんでした')
    return l_poke
