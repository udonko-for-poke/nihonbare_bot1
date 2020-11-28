import discord
from discord.ext import commands
import os
import sys
import re
sys.path.append(os.path.join(os.path.dirname(__file__), 'Commands'))
import cmd_roles
import cmd_raid
import cmd_card
import cmd_status
import cmd_sql
import cmd_home
import cmd_system
import vc

SERVERID     = 696651369221718077       #鯖ID
SLAVE_ID     = 723507961816678420       #役職：レイドの奴隷のID
CALL_ID      = 753655891114590348       #役職：通話通知のID
CALL_CHANNEL = 753655481322569808       #通話通知を飛ばすチャンネルのID
FOR_BOT      = 765392422829162556       #SQL文の実行を許可するチャンネル
BKP_CHANNEL  = 782065499696922634       #バックアップを送るチャンネル
MY_SERVER    = 539750441479831573       #実験用鯖1
MY_SERVER2   = 723833856871891004       #実験用鯖2
HOST_ROLE    = 696655902438326292       #役職：HOSTのID
vc_state     = 0                        #ボイスチャンネルにいる人の数を0で初期化
NOT_MENTION  = [699547606728048700]     #通話が始まっても通知しないチャンネル

MAINPATH   = os.path.dirname(os.path.abspath(__file__)) #このファイルの位置
TOKEN_PATH = '' + MAINPATH + '/Data/BotID.txt'          #TOKENが保存されているファイル
STOCK_PATH = '' + MAINPATH + '/Data/Stock.txt'          #レイドの在庫が保存されているファイル
IMG_PATH   = '' + MAINPATH + '/Commands/IMG/'           #画像が保存されているファイル
SQLCMD_PATH = '' + MAINPATH + '/Data/cmdsql.pickle'     #登録済みのSQL文が保存されているファイル

#TOKENの読み込み
with open(TOKEN_PATH, "r",encoding="utf-8_sig") as f:
    l = f.readlines()
    l_strip = [s.strip() for s in l]
    TOKEN = l_strip[0]

#在庫の読み込み
with open(STOCK_PATH, "r",encoding="utf-8_sig") as f:
    l = f.readlines()
    l_poke = [s.strip() for s in l]

# "!"から始まるものをコマンドと認識する
prefix = '!'
#helpコマンドの日本語化
class JapaneseHelpCommand(commands.DefaultHelpCommand):
    def __init__(self):
        super().__init__()
        self.commands_heading = "コマンド:"
        self.no_category = "その他"
        self.command_attrs["help"] = "コマンド一覧と簡単な説明を表示"

    def get_ending_note(self):
        return (f"各コマンドの説明: {prefix}help <コマンド名>\n"
                f"各カテゴリの説明: {prefix}help <カテゴリ名>\n")

#botの作成
bot = commands.Bot(command_prefix='!', help_command=JapaneseHelpCommand())

# bot起動時に"login"と表示
@bot.event
async def on_ready():
    activity = discord.Activity(name='Python', type=discord.ActivityType.playing)
    await bot.change_presence(activity=activity)
    print('login\n')

#コマンドに関するエラー
@bot.event
async def on_command_error(ctx, error):
    print(type(error))
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send(f'{ctx.author.mention}エラー：引数の数が不正です')
        return

    if isinstance(error, commands.errors.CommandNotFound):
        await ctx.send(f'{ctx.author.mention}エラー：コマンドが見つかりません')
        return
    print(error)
    raise error

#botが自分自身を区別するための関数
def is_me(m):
    return m.author == bot.user

async def send_message(send_method, mention, mes):
    if (type(mes) is list):
        if (len(mes) == 0):
            await send_method(f'{mention} 該当するデータがありません')
        elif (len(mes) == 1):
            await send_method(f'{mention} ' + str(mes[0]))
        else:
            reply = ''
            for data in mes:
                reply += data+'\n'
            try:
                embed = discord.Embed(title="Result",description=reply)
                await send_method(f'{mention} ', embed=embed)
            except:
                await send_method(f'{mention} エラー：該当するデータが多すぎます')
    elif (type(mes) is str):
        if (len(mes) == 0):
            await send_method(f'{mention} 該当するデータがありません')
        else:
            await send_method(f'{mention} ' + str(mes))
    else:
        pass
    return

class __Roles(commands.Cog, name = '役職の管理'):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        
    @commands.command()
    # 役職の付与
    async def add(self, ctx, role):
        """役職を付与：slave->レイドの奴隷、call->通話通知"""
        await cmd_roles.add(ctx, role)
        return
        
    # 役職の解除
    @commands.command()
    async def rm(self, ctx, role):
        """役職を解除"""
        await cmd_roles.rm(ctx, role)
        return

class __Raid(commands.Cog, name = 'レイド関連'):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    # 在庫の確認
    @commands.command()
    async def check(self, ctx, poke):
        """レイドが開催済みかどうかを検索"""
        global l_poke
        await cmd_raid.process_raid_check(ctx, poke, l_poke)
        
    @commands.command()
    async def store(self, ctx, poke):
        """開催済みレイドの追加"""
        global l_poke
        l_poke = await cmd_raid.process_raid_add(ctx, poke, STOCK_PATH, l_poke)        

    @commands.command()
    async def raid(self, ctx, cmd, poke):
        """レイド関連のコマンド：add->store, check, del:削除（HOSTのみ使用可)"""
        global l_poke
        if (cmd == 'add'):
            l_poke = await cmd_raid.process_raid_add(ctx, poke, STOCK_PATH, l_poke)
            return
        if (cmd == 'check'):
            await cmd_raid.process_raid_check(ctx, poke, l_poke)
            return
        if (cmd == 'del'):
            l_poke = await cmd_raid.process_raid_del(ctx, poke, STOCK_PATH, l_poke)
            return
        return

@bot.command()
async def card(ctx, *pokes):
    """簡易な構築の画像を生成"""
    await cmd_card.makecard(ctx, pokes, IMG_PATH)
    return
        
@bot.command()
async def bkp(ctx):
    """botのデータのバックアップを取る"""
    if (ctx.message.author.top_role.id != HOST_ROLE):
        await ctx.send(f'{ctx.author.mention} 権限が足りません')
        return
    global MAINPATH
    channel  = bot.get_channel(BKP_CHANNEL)
    filelist = ['Stock.txt', 'cmdsql.pickle']
    result = await cmd_system.bkp(channel.send, filelist, MAINPATH+'/Data')
    if (result):
        mes = 'バックアップを取りました'
    else:
        mes = 'バックアップに失敗しました'
    await ctx.send(f'{ctx.author.mention} ' + mes)
    return

#################################
#SQLite
#################################
class __Status(commands.Cog, name = '数値確認'):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
    ##  種族値、実数値の表示
    @commands.command()
    async def st(self, ctx, *pokedata):
        """種族値の表示，数値を書くと該当Lvでの実数値を表示"""
        await cmd_status.st(ctx, pokedata)
        return

    @commands.command()
    async def korippo(self, ctx, poke):
        """コオリッポ算"""
        await cmd_status.korippo(ctx, poke)
        return

    @commands.command()
    async def calciv(self, ctx, poke, lv, *args):
        """個体値チェック"""
        await cmd_status.calciv(ctx, poke, lv, args)
        return

class __SQL(commands.Cog, name = 'SQL'):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @commands.command()
    async def addsql(self, ctx, *cmd_SQL):
        """新規SQL文の登録"""
        await cmd_sql.addsql(ctx, cmd_SQL, SQLCMD_PATH)
        return
      
    @commands.command()
    async def showsql(self, ctx, *cmd_SQL):
        """登録済みSQL文の表示"""
        await cmd_sql.showsql(ctx, cmd_SQL, SQLCMD_PATH)
        return

    @commands.command()
    async def delsql(self, ctx, cmd):
        """登録済みSQL文の削除"""
        await cmd_sql.delsql(ctx, cmd, SQLCMD_PATH)
        return

class __Home(commands.Cog, name = 'Home'):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    def getbattlerule(self, args, argnum):
        battlerule = 1
        rate = []
        if (len(args) == argnum+1):
            for i in range(argnum):
                rate.append(args[i+1])
            if (args[0] == '2' or args[0] == '1'):
                battlerule = int(args[0])
            else:
                return [-1], None
        elif (len(args) == argnum):
            for i in range(argnum):
                rate.append(args[i])
        else:
            return [-2], None
        try:
            intrate = [int(i) for i in rate]
        except:
            return [-3], None
        return intrate, battlerule
        
    def getbattlerulestr(self, args, argnum):
        battlerule = 1
        s = []
        if (len(args) == argnum+1):
            for i in range(argnum):
                s.append(args[i+1])
            if (args[0] == '2' or args[0] == '1'):
                battlerule = int(args[0])
            else:
                return [-1], None
        elif (len(args) == argnum):
            for i in range(argnum):
                s.append(args[i])
        else:
            return [-2], None
        return s, battlerule
    
    async def printerror(self, ctx):
        await ctx.send(f'{ctx.author.mention} 引数が間違っています')
        return
    
    @commands.command()
    async def rank(self, ctx, *battlerule_rate):
        """レートに対応する順位を求める"""
        rate, battlerule = self.getbattlerule(battlerule_rate, 1)
        if (battlerule == None):
            await self.printerror(ctx)
            return
        rate = rate[0]
        print('rank:'+str(rate))
        success = await cmd_home.get_rank(ctx, rate, battlerule)
        if (success == 0):
            await send_message(ctx.send, ctx.author.mention, 'データの取得に失敗しました')
            return
        return

    @commands.command()
    async def rate(self, ctx, *battlerule_rank):
        """順位に対応するレートを求める"""
        rank, battlerule = self.getbattlerule(battlerule_rank, 1)
        if (battlerule == None):
            await self.printerror(ctx)
            return
        rank = rank[0]
        print('rate:'+str(rank))
        success = await cmd_home.get_rate(ctx, rank, battlerule)
        if (success == 0):
            await send_message(ctx.send, ctx.author.mention, 'データの取得に失敗しました')
            return
        return

    @commands.command()
    async def pokerank(self, ctx, *battlerule_upper_lower):
        """ポケモンの使用率を求める"""
        rank, battlerule = self.getbattlerule(battlerule_upper_lower, 2)
        if (battlerule == None):
            await self.printerror(ctx)
            return
        print('pokerank:'+str(rank))
        pokelist, update_time = await cmd_home.pokerank(ctx, rank, battlerule)
        if (len(pokelist) <= 0):
            await send_message(ctx.send, ctx.author.mention, 'No data('+update_time+')')
            return
        await send_message(ctx.send, ctx.author.mention, pokelist)
        await send_message(ctx.send, '', '('+update_time+')')
        return

    @commands.command()
    async def pokeinfo(self, ctx, *battle_rule_pokename):
        """ホームのポケモンの情報を求める"""
        name, battlerule = self.getbattlerulestr(battle_rule_pokename, 1)
        print('pokeinfo:'+str(name))
        if (battlerule == None):
            await self.printerror(ctx)
            return
        res, update_time = await cmd_home.pokeinfo(ctx, name[0], battlerule)
        if (len(res) <= 0):
            await send_message(ctx.send, ctx.author.mention, 'No data('+update_time+')')
            return
        print(update_time)
        await send_message(ctx.send, '', '('+update_time+')')
        return
##  改行を伴うコマンドの受け付け
@bot.event
async def on_message(message):
    head = message.content[:11].lower()
    if head == '!sql select':
        await cmd_sql.playsql(message, MY_SERVER, MY_SERVER2, FOR_BOT)
        return
    head = message.content[:9].lower()
    if head == '!editsql ':
        await cmd_sql.editsql(message, SQLCMD_PATH)
        return
    if(message.content.startswith('?')):
        await cmd_sql.registered_sql(message, SQLCMD_PATH)
        return
    await bot.process_commands(message)
    return

#発言の削除
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
bot.add_cog(__Home(bot=bot))
bot.run(TOKEN)
