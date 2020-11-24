import discord
from discord.ext import commands
import os
import sys
import jaconv
import re
import pickle
sys.path.append(os.path.join(os.path.dirname(__file__), 'Functions'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'SQLite'))
import rolls
import vc
import calc
import raid as raidcommands
import image_

SERVERID = 696651369221718077
SLAVE_ID = 723507961816678420
CALL_ID  = 753655891114590348
CALL_CHANNEL = 753655481322569808
FOR_BOT  = 765392422829162556
MY_SERVER = 539750441479831573
MY_SERVER2= 723833856871891004
HOST_ROLE = 696655902438326292
#CHANNELLIST = [696651369662119976, 696652749873479700, 696652871562690607]
vc_state = 0
# 例外設定
NOT_MENTION = [699547606728048700]

TOKEN_PATH = '' + os.path.dirname(os.path.abspath(__file__)) + '/Data/BotID.txt'
STOCK_PATH = '' + os.path.dirname(os.path.abspath(__file__)) + '/Data/Stock.txt'
IMG_PATH   = '' + os.path.dirname(os.path.abspath(__file__)) + '/Functions/IMG/'
CMD_PATH = '' + os.path.dirname(os.path.abspath(__file__)) + '/Data/cmd.txt'
SQLCMD_PATH = '' + os.path.dirname(os.path.abspath(__file__)) + '/Data/cmdsql.pickle'

with open(TOKEN_PATH, "r",encoding="utf-8_sig") as f:
    l = f.readlines()
    l_strip = [s.strip() for s in l]
    TOKEN = l_strip[0]

with open(STOCK_PATH, "r",encoding="utf-8_sig") as f:
#    STATE_PATH = '' + os.path.dirname(os.path.abspath(__file__)) + '/Data/state.txt'
    l = f.readlines()
    l_poke = [s.strip() for s in l]

# "!"から始まるものをコマンドと認識する
#bot = commands.Bot(command_prefix='!')
prefix = '!'
class JapaneseHelpCommand(commands.DefaultHelpCommand):
    def __init__(self):
        super().__init__()
        self.commands_heading = "コマンド:"
        self.no_category = "その他"
        self.command_attrs["help"] = "コマンド一覧と簡単な説明を表示"

    def get_ending_note(self):
        return (f"各コマンドの説明: {prefix}help <コマンド名>\n"
                f"各カテゴリの説明: {prefix}help <カテゴリ名>\n")

bot = commands.Bot(command_prefix='!', help_command=JapaneseHelpCommand())

def is_me(m):
    return m.author == bot.user

# bot起動時に"login"と表示
@bot.event
async def on_ready():
    activity = discord.Activity(name='Python', type=discord.ActivityType.playing)
    await bot.change_presence(activity=activity)
    print('login\n')

@bot.event
async def on_command_error(ctx, error):
    print(type(error))
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send(f'{ctx.author.mention}エラー：引数の数が不正です')
        return

    if isinstance(error, commands.errors.CommandNotFound):
        await ctx.send(f'{ctx.author.mention}エラー：コマンドが見つかりません')
        return

    # If nothing is caught, reraise the error so that it goes to console.
    raise error

class __Roles(commands.Cog, name = '役職の管理'):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        
    @commands.command()
    # 役職の付与
    async def add(self, ctx, arg):
        """役職を付与：slave->レイドの奴隷、call->通話通知"""
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
    @commands.command()
    async def rm(self, ctx, arg):
        """役職を解除"""
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

class __Raid(commands.Cog, name = 'レイド関連'):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    # 在庫の確認
    @commands.command()
    async def check(self, ctx, arg):
        """レイドが開催済みかどうかを検索"""
        global l_poke
        await raidcommands.process_raid_check(ctx, arg, l_poke)
        
    @commands.command()
    async def store(self, ctx, arg):
        """開催済みレイドの追加"""
        global l_poke
        await raidcommands.process_raid_add(ctx, arg, STOCK_PATH, l_poke)        

    @commands.command()
    async def raid(self, ctx, arg1, arg2):
        """レイド関連のコマンド：add->store, check, del:削除（HOSTのみ使用可)"""
        global l_poke
        if (arg1 == 'add'):
            await raidcommands.process_raid_add(ctx, arg2, STOCK_PATH, l_poke)
            return
        if (arg1 == 'check'):
            await raidcommands.process_raid_check(ctx, arg2, l_poke)
            return
        if (arg1 == 'del'):
            if (ctx.message.author.top_role.id == HOST_ROLE):
                await raidcommands.process_raid_del(ctx, arg2, STOCK_PATH, l_poke)
            else:
                await ctx.send(f'{ctx.author.mention} 権限が足りません')
            return

@bot.command()
async def card(ctx, *arg):
    """簡易な構築の画像を生成"""
    icon_size = 60
    import getSQL
    from PIL import Image, ImageDraw
    result = await ctx.message.author.avatar_url.save(IMG_PATH+'user.png', seek_begin = True)
    pokel = []
    for p in arg:
        pokel.append(p)
    if (len(pokel) > 6):
        pokel = pokel[:6]
    pokes  = tuple(pokel)
    numbers= []
    #ポケモン名からIDを探してリストに格納
    c_flg = 0   #ポケモン名が一致しなかった場合にTrueになる
    candidate = ''  #一致しないポケモンの候補
    for poke in pokes:
        if (poke == 'null'):
            numbers.append('NULL')
        else:
            result2 = await getSQL.poke2num(poke)
            if (result2 == ''):
            
                result = await getSQL.inname(poke)
                if (result[1] == -1 or result[1] >= 10):
                    pass
                else:
                    candidate += result[0] + '\n'
                    c_flg = 1
                continue
            numbers.append(result2 + '.gif')
    
    base_url = 'https://78npc3br.user.webaccel.jp/poke/icon96/n'
    
    #   背景の作成
    im = Image.new("RGB", (400, 225), (128, 128, 128))
    draw = ImageDraw.Draw(im)
    img_clear = Image.new("RGBA", im.size, (255, 255, 255, 0))

    i = 0       
    for no in numbers:
        if (no != 'NULL'):
            result3 = await image_.dl(base_url + no, IMG_PATH + no)
            #IDを使ってDL
            if (result3):
                poke_im = Image.open(IMG_PATH+no)
                img_clear.paste(poke_im, ((i%3)*100+75, (i//3)*100+25))
                i += 1
                del(poke_im)
        else:
            i += 1
                    
    im.paste(img_clear, mask=img_clear.split()[3])
    im1 = Image.open(IMG_PATH+'user.png')
    im1 = im1.resize((icon_size,icon_size))
    mask_im = Image.new("L", im1.size, 0)
    draw = ImageDraw.Draw(mask_im)
    draw.ellipse((0, 0, icon_size, icon_size), fill=255)
    
#    draw2 = ImageDraw.Draw(im)
#    for i in range(3):
#        draw2.line((75, 25+i*100, 375, 25+i*100), fill=(255, 255, 255), width=4)
#    for i in range(4):
#        draw2.line((75+i*100, 25, 75+i*100, 225), fill=(255, 255, 255), width=4)
    
    im.paste(im1, (20,20), mask_im)
    im.save(IMG_PATH+'out.jpg', quality=95)
    numbers.append('out.jpg')
    numbers.append('user.png')
    file_img = discord.File(IMG_PATH+'out.jpg')
    
    await ctx.message.delete()
    await ctx.send(file=file_img)
    
    if(c_flg):
        embed = discord.Embed(title="もしかして",description=candidate)
        await ctx.send(f'{ctx.author.mention} ', embed=embed)
    del(im1)
    del(file_img)
    if ('NULL' in numbers):
        numbers = numbers.remove('NULL')
    numbers = list(set(numbers))
    for f in numbers:
        os.remove(IMG_PATH+f)
        
#################################
#SQLite
#################################
class __Status(commands.Cog, name = '数値確認'):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
    ##  種族値、実数値の表示
    @commands.command()
    async def st(self, ctx, *arg1):
        """種族値の表示，数値を書くと該当Lvでの実数値を表示"""
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

    @commands.command()
    async def korippo(self, ctx, poke):
        """コオリッポ算"""
        import getSQL
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

    @commands.command()
    async def calciv(self, ctx, poke, lv, *args):
        """個体値チェック"""
        print('calciv'+poke)
        st_list, check_list = [], []
        #引数の中に個体値チェックの箇所指定があるかどうかの確認
        for x in args:
            try:
                st_list.append(int(x))
            except ValueError:
                txt = x.upper()
                if (re.fullmatch(r'[A-DHS]', txt)):
                        check_list.append(txt)
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
                
            from SQLite import getSQL
            txt = 'SELECT ' +  ','.join(check_list) + ' FROM pokemon WHERE name = ?'
            result = await getSQL.getivs(poke, txt, lv, st_list, check_h)
            if (not result):
                await ctx.send(f'{ctx.author.mention} エラー：'+poke+'が見つかりませんでした')
            else:
                await ctx.send(f'{ctx.author.mention}\n' + result)
        return

class __SQL(commands.Cog, name = 'SQL'):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @commands.command()
    async def addsql(self, ctx, *arg):
        """新規SQL文の登録"""
        if (len(arg) <= 1):
            await ctx.send(f'{ctx.author.mention} エラー：コマンドが短すぎます')
            return
        cmd = arg[0]
        text = ''
        info=''
        flg = 0
        for i in range(len(arg)-1):
           text += arg[i+1] + ' '
        
        if (text.startswith('select') or text.startswith('SELECT')):
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
      
    @commands.command()
    async def showsql(self, ctx, *arg):
        """登録済みSQL文の表示"""
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

    @commands.command()
    async def delsql(self, ctx, cmd):
        """登録済みSQL文の削除"""
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

async def sqlreq(message, cmd, argtpl):
    import getSQL
    print('SQL request->'+cmd+','+str(argtpl))
    result = await getSQL.sqlrequest(cmd, argtpl)
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
            await sqlreq(message, arg1, argtpl)
            return
            
    elif(message.content.startswith('!editsql ') or message.content.startswith('!editsql　')):
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

    elif(message.content.startswith('?')):
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
        
    else:
        await bot.process_commands(message)

@bot.event
async def on_raw_reaction_add(payload):
    if (payload.emoji.name == '8jyomei'):
        channel = bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if (is_me(message)):
            await message.delete()
            print(payload.member.name + ' has deleted bot comment')
        
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
        
bot.add_cog(__Roles(bot=bot))
bot.add_cog(__Raid(bot=bot))
bot.add_cog(__Status(bot=bot))
bot.add_cog(__SQL(bot=bot))
bot.run(TOKEN)
