import discord

async def Edit_role(ctx, role, opt):
    member = ctx.author
    if (opt):
        await member.add_roles(role)
        print(str(ctx.message.author.name)+'->'+str(role))
        await ctx.send(f'{ctx.author.mention} 役職を追加しました')
    else:
        await member.remove_roles(role)
        print(str(ctx.message.author.name)+'->'+str(role)+'(remove)')
        await ctx.send(f'{ctx.author.mention} 役職を削除しました')
    return

