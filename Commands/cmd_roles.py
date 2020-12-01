import rolls

#役職の付与
async def add(ctx, arg):
    opt = 1
    if (arg == 'slave'):
        role = ctx.message.guild.get_role(SLAVE_ID)
        await rolls.Edit_role(ctx, role, opt)
        flg = 0
    if (arg == 'call'):
        role = ctx.message.guild.get_role(CALL_ID)
        await rolls.Edit_role(ctx, role, opt)
        flg = 0
    if (flg):
        await ctx.send(f'{ctx.author.mention} '+arg+'オプションは実装されていません\n実装済みのオプション：\'slave\', \'call\'')
    return 1

async def rm(ctx, arg):
    opt = 0
    flg = 1
    if (arg == 'slave'):
        role = ctx.message.guild.get_role(SLAVE_ID)
        await rolls.Edit_role(ctx, role, opt)
        flg = 0
    if (arg == 'call'):
        role = ctx.message.guild.get_role(CALL_ID)
        await rolls.Edit_role(ctx, role, opt)
        flg = 0
    if (flg):
        await ctx.send(f'{ctx.author.mention} '+arg+'オプションは実装されていません\n実装済みのオプション：\'slave\', \'call\'')
    return