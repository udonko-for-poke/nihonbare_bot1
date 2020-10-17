import discord
from discord.ext import commands
import os
import sys
import jaconv
import re
sys.path.append(os.path.join(os.path.dirname(__file__), 'Functions'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'SQLite'))
import rolls
import vc
import raid as raidcommands

SERVERID = 696651369221718077
SLAVE_ID = 723507961816678420
CALL_ID  = 753655891114590348
CALL_CHANNEL = 753655481322569808
FOR_BOT  = 765392422829162556
MY_SERVER = 539750441479831573
MY_SERVER2= 723833856871891004
#CHANNELLIST = [696651369662119976, 696652749873479700, 696652871562690607]
vc_state = 0
# 例外設定
NOT_MENTION = [699547606728048700]

TOKEN_PATH = '' + os.path.dirname(os.path.abspath(__file__)) + '/Data/BotID.txt'
STOCK_PATH = '' + os.path.dirname(os.path.abspath(__file__)) + '/Data/Stock.txt'
CMD_PATH = '' + os.path.dirname(os.path.abspath(__file__)) + '/Data/cmd.txt'

with open(TOKEN_PATH, "r",encoding="utf-8_sig") as f:
    l = f.readlines()
    l_strip = [s.strip() for s in l]
    TOKEN = l_strip[0]

with open(STOCK_PATH, "r",encoding="utf-8_sig") as f:
#    STATE_PATH = '' + os.path.dirname(os.path.abspath(__file__)) + '\\Data\\state.txt'
    l = f.readlines()
    l_poke = [s.strip() for s in l]

# "!"から始まるものをコマンドと認識する
bot = commands.Bot(command_prefix='!')


# bot起動時に"login"と表示
@bot.event
async def on_ready():
    activity = discord.Activity(name='Python', type=discord.ActivityType.playing)
#    activity = discord.Activity(name='Pythonが板', type=discord.ActivityType.custom)
    await bot.change_presence(activity=activity)
    print('login\n')


# メッセージ受信時
@bot.command()
# 役職の付与
async def add(ctx, arg):
    opt = 1
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
    
# 役職の解除
@bot.command()
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

#コマンド一覧
@bot.command()
async def cmd(ctx):
    print('!cmd')
    with open(CMD_PATH, "r",encoding="utf-8_sig") as f:
        txt = f.read()
        await ctx.send(f'{ctx.author.mention} \n'+txt)

# 在庫の確認
@bot.command()
async def check(ctx, arg):
    global l_poke
    await raidcommands.process_raid_check(ctx, arg, l_poke)
    
# 在庫の追加        
@bot.command()
async def addraid(ctx, arg):
    global l_poke
    await raidcommands.process_raid_add(ctx, arg, STOCK_PATH, l_poke)
    

@bot.command()
async def raid(ctx, arg1, arg2):
    global l_poke
    if (arg1 == 'add'):
        await raidcommands.process_raid_add(ctx, arg2, STOCK_PATH, l_poke)
        return
    if (arg1 == 'check'):
        await raidcommands.process_raid_check(ctx, arg2, l_poke)
        return

# 在庫の追加        
@bot.command()
async def store(ctx, arg):
    global l_poke
    await raidcommands.process_raid_add(ctx, arg, STOCK_PATH, l_poke)
        
#################################
#SQLite
#################################
@bot.command()
async def status(ctx, arg, arg2):
    import getSQL
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
    poke = jaconv.hira2kata(poke).replace('２', '2')
    print('status->'+poke+','+str(isreal))
    result = await getSQL.getstatus('name', poke, isreal)
    if (not result[0]):
        await ctx.send(f'{ctx.author.mention} '+result[1])
    else:
        await ctx.send(f'{ctx.author.mention} エラー：'+arg[1]+'が見つかりませんでした')
    return
   
##  種族値、実数値の表示
@bot.command()
async def st(ctx, *arg1):
    import getSQL
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
    poke = jaconv.hira2kata(poke).replace('２', '2')
    print('status->'+poke+','+str(isreal))
    #   数値を取得
    result = await getSQL.getstatus('name', poke, isreal)
    if (not result[0]):
        await ctx.send(f'{ctx.author.mention} \n'+result[1])
    else:
        await ctx.send(f'{ctx.author.mention} エラー：'+poke+'が見つかりませんでした')
    return
   
##  改行を伴うコマンドの受け付け
@bot.event
async def on_message(message):
    if message.content.startswith('!sql SELECT') or message.content.startswith('!sql select'):
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
            import getSQL
            print('SQL request->'+arg1+','+str(argtpl))
            result = await getSQL.sqlrequest(arg1, argtpl)
            if (result[1] == -1):
                await  message.channel.send(f'{message.author.mention} 該当するデータが見つかりませんでした')
            else:
                print('len='+str(result[1]))
    #            print(result[0])
                if (result[1] >= 5990):
                    await  message.channel.send(f'{message.author.mention} 該当するデータが多すぎます\n('+str(result[1])+'/6000字)')
                else:
                    embed = discord.Embed(title="Result",description=result[0])
                    print('embed_len = '+str(len(embed)))
    #                print('?')
    #                print(result[0])
                    await message.channel.send(f'{message.author.mention} ', embed=embed)
    else:
        await bot.process_commands(message)

################################
#VC
################################
@bot.event
async def on_voice_state_update(member, before, after):
    global vc_state
    global NOT_MENTION
    result = await vc.move_member(member, before, after, SERVERID, NOT_MENTION)
    vc_state += result[0]
    if (result[1] == 1 and vc_state == 1):
        print('通話開始')
        channel = bot.get_channel(CALL_CHANNEL)
        role = bot.get_guild(SERVERID ).get_role(CALL_ID)
        await channel.send(f'{role.mention} 通話が始まりました')
bot.run(TOKEN)

