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
sys.path.append(os.path.join(os.path.dirname(__file__), 'Commands/Functions'))
import vc

SERVERID = 696651369221718077       #鯖ID
CALL_CHANNEL = 753655481322569808   #通話通知を飛ばすチャンネルのID
FOR_BOT  = 765392422829162556       #SQL文の実行を許可するチャンネル
MY_SERVER = 539750441479831573      #実験用鯖1
MY_SERVER2= 723833856871891004      #実験用鯖2
HOST_ROLE = 696655902438326292      #役職：HOSTのID
vc_state = 0                        #ボイスチャンネルにいる人の数を0で初期化
NOT_MENTION = [699547606728048700]  #通話が始まっても通知しないチャンネル

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
    raise error

#botが自分自身を区別するための関数
def is_me(m):
    return m.author == bot.user

class __Roles(commands.Cog, name = '役職の管理'):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        
    @commands.command()
    # 役職の付与
    async def add(self, ctx, arg):
        """役職を付与：slave->レイドの奴隷、call->通話通知"""
        await cmd_roles.add(ctx, arg)
        return
        
    # 役職の解除
    @commands.command()
    async def rm(self, ctx, arg):
        """役職を解除"""
        await cmd_roles.rm(ctx, arg)
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
        await cmd_raid.process_raid_check(ctx, arg, l_poke)
        
    @commands.command()
    async def store(self, ctx, arg):
        """開催済みレイドの追加"""
        global l_poke
        l_poke = await cmd_raid.process_raid_add(ctx, arg, STOCK_PATH, l_poke)        

    @commands.command()
    async def raid(self, ctx, arg1, arg2):
        """レイド関連のコマンド：add->store, check, del:削除（HOSTのみ使用可)"""
        global l_poke
        if (arg1 == 'add'):
            l_poke = await cmd_raid.process_raid_add(ctx, arg2, STOCK_PATH, l_poke)
            return
        if (arg1 == 'check'):
            await cmd_raid.process_raid_check(ctx, arg2, l_poke)
            return
        if (arg1 == 'del'):
            l_poke = await cmd_raid.process_raid_del(ctx, arg2, STOCK_PATH, l_poke)
            return
        return

@bot.command()
async def card(ctx, *arg):
    """簡易な構築の画像を生成"""
    await cmd_card.makecard(ctx, arg, IMG_PATH)
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
    async def st(self, ctx, *arg):
        """種族値の表示，数値を書くと該当Lvでの実数値を表示"""
        await cmd_status.st(ctx, arg)
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
    async def addsql(self, ctx, *arg):
        """新規SQL文の登録"""
        await cmd_sql.addsql(ctx, arg, SQLCMD_PATH)
        return
      
    @commands.command()
    async def showsql(self, ctx, *arg):
        """登録済みSQL文の表示"""
        await cmd_sql.showsql(ctx, arg, SQLCMD_PATH)
        return

    @commands.command()
    async def delsql(self, ctx, cmd):
        """登録済みSQL文の削除"""
        await cmd_sql.delsql(ctx, cmd, SQLCMD_PATH)
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
bot.run(TOKEN)
