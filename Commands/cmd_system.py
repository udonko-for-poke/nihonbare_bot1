import discord

async def bkp(ch_send, filelist, fpath):
#    try:
        for f in filelist:
            await ch_send(file=discord.File(fpath+'/'+f))
        return 1
#    except:
#        return 0