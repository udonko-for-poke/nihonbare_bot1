async def move_member(member, before, after, SERVERID, NOT_MENTION):
    vc_state = 0
    isSend = 0
    txt = ''+str(member)+'->'
    if (before.channel is not None):
        if (before.channel.guild.id != SERVERID):
            print(''+str(member)+'->にほんばれサーバーの外側から移動しました')
            return 0, 0
    if (after.channel is not None):
        if (after.channel.guild.id != SERVERID):
            print(''+str(member)+'->にほんばれサーバーの外側へ移動しました')
            return 0, 0
    # チャンネルを移動していない場合処理をしない
    if (before.channel == after.channel):
        return 0, 0
        
    # チャンネルから退出してきた場合
    if before.channel is not None:
        txt += str(before.channel)+' → '
        # ボイスチャンネルに誰もいなくなった場合
        flg = 0
        for x in NOT_MENTION:
            if (before.channel.id == x):
                flg = 1
        
        if ((flg == 0) and (len(before.channel.members) == 0)):
            vc_state -= 1
    else:
        txt += 'None → '
    # ボイスチャンネルに参加してきた場合
    if after.channel is not None:
        txt += str(before.channel)
        flg = 0
        for x in NOT_MENTION:
            if (after.channel.id == x):
                flg = 1
        # 参加したチャンネルの1人目だった場合
        if ((flg == 0) and (len(after.channel.members) == 1)):
            
            vc_state += 1
            if (vc_state == 1):
                isSend = 1
#                await channel.send(f'{role.mention} 通話が始まりました')
    else:
        txt += 'None'
    print(txt)
    return vc_state, isSend