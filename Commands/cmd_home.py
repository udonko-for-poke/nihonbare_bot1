import urllib.request
import json
import gzip
import os
import datetime
import pickle
import discord


def load_update_time(battle_rule):
    fpath = os.path.dirname(os.path.abspath(__file__))+'/HomeUpdateTime'+str(battle_rule)+'.txt'
    ts = [0,0]
    if (os.path.exists(fpath)):
        with open(fpath, 'r') as f:
            data = f.read()
        ts_str = data.split(',')
        ts = [int(ts_str[0]), int(ts_str[1])]
    return ts

def save_update_time(ts, battle_rule):
    fpath = os.path.dirname(os.path.abspath(__file__))+'/HomeUpdateTime'+str(battle_rule)+'.txt'
    ts_str = str(ts[0])+','+str(ts[1])
    with open(fpath, 'w') as f:
        f.write(ts_str)
    return

def calc_seasonid(season, battle_rule):
    return 10000 + season * 10 + battle_rule

def ranking_search(_list, value_):
    length = len(_list)
    value = value_*1000
    if (_list[0] < value):
        return 0
    if (_list[length-1] > value):
        return length
    rank = 0
    if (_list[length//2] < value):
        rank = ranking_search(_list[:length//2], value_)
    else:
        rank = (length//2)+ranking_search(_list[length//2:], value_)
    return rank

async def create_request(battle_rule):
    url = 'https://api.battle.pokemon-home.com/cbd/competition/rankmatch/list'
    req_header = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'countrycode': '304',
        'authorization': 'Bearer',
        'langcode': '1',
        'user-agent': 'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Mobile Safari/537.36',
        'content-type': 'application/json',}
    req_data = {'soft': 'Sw',}
    req = urllib.request.Request(url, json.dumps(req_data).encode(), req_header)
    body = ''
    
    try:
        with urllib.request.urlopen(req) as response:
            body = json.load(response)

    except urllib.error.URLError as e:
        print(e.reason)
    season = int(list(body['list'].keys())[0])
    season_id = calc_seasonid(season, battle_rule)
    detail = body['list'][str(season)][str(season_id)]
    return [detail['ts1'], detail['ts2']], detail['rst'], season_id

def load_trainer(battle_rule):
    MAINPATH = os.path.dirname(os.path.abspath(__file__))
    body = ''
    with gzip.open(MAINPATH+'/trainer'+str(battle_rule)+'.json.gz', mode='rt', encoding='utf-8') as f:
        data = f.read()
        body = json.loads(data)
    rate = []
    for r in body:
        rate.append(int(r['rating_value']))
    return rate

def load_pokerank(rank, battle_rule):
    MAINPATH = os.path.dirname(os.path.abspath(__file__))
    body = ''
    with open(MAINPATH+'/pokerank'+str(battle_rule)+'.pickle', 'rb') as f:
        body = pickle.load(f)
    
    with open(MAINPATH+'/pokedex.pickle', 'rb') as f:
        pokedex = pickle.load(f)
        pokenames = pokedex['poke']
    del(pokedex)
    pokerank = []
    lower = min(max(rank), len(body))
    upper = max(1, min(rank))
    if (lower < upper):
        return []
    upper -= 1
    for i in range(upper, lower):
        r = body[i]
        pokename = pokenames[int(r['id'])-1]
        if (r['form'] != 0):
            pokename += '(form='+str(r['form'])+')'
        pokerank.append(pokename)
    return pokerank

def load_pokeinfo(pokename, battle_rule):
    MAINPATH = os.path.dirname(os.path.abspath(__file__))
    body = ''
    with open(MAINPATH+'/pokerank'+str(battle_rule)+'.pickle', 'rb') as f:
        body = pickle.load(f)
    
    with open(MAINPATH+'/pokedex.pickle', 'rb') as f:
        pokedex = pickle.load(f)
        pokenames = pokedex['poke']
    del(pokedex)
    pokerank = []
    lower = min(max(rank), len(body))
    upper = max(1, min(rank))
    if (lower < upper):
        return []
    upper -= 1
    for i in range(upper, lower):
        r = body[i]
        pokename = pokenames[int(r['id'])-1]
        if (r['form'] != 0):
            pokename += '(form='+str(r['form'])+')'
        pokerank.append(pokename)
    return pokerank

async def get_trainer(ts, rst, season_id, battle_rule):
    url = 'https://resource.pokemon-home.com/battledata/ranking/'+str(season_id)+'/'+str(rst)+'/'+str(ts)+'/traner-1'
    MAINPATH = os.path.dirname(os.path.abspath(__file__))
    try:
        with urllib.request.urlopen(url) as web_file:
            data = web_file.read()
            with open(MAINPATH+'/trainer'+str(battle_rule)+'.json.gz', mode='wb') as local_file:
                local_file.write(data)
    except urllib.error.URLError as e:
        print(e)
        return 0
    return 1

async def get_pokerank(ts, rst, season_id, battle_rule):
    url = 'https://resource.pokemon-home.com/battledata/ranking/'+str(season_id)+'/'+str(rst)+'/'+str(ts)+'/pokemon'
    MAINPATH = os.path.dirname(os.path.abspath(__file__))
    req_header = {
        'user-agent': 'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Mobile Safari/537.36',
        'accept': 'application/json',
    }
    req = urllib.request.Request(url, headers=req_header)
    with urllib.request.urlopen(req) as res:
        detail = json.load(res)
    with open(MAINPATH+'/pokerank'+str(battle_rule)+'.pickle', 'wb') as f:
        pickle.dump(detail, f)
    req_header = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Mobile Safari/537.36',
        'countrycode': '304',
        'authorization': 'Bearer',
        'langcode': '1',
        'accept': 'application/json, text/javascript, */*; q=0.01',
    }
    pokedata = {}
    for i in range(1, 6):
        url = f'https://resource.pokemon-home.com/battledata/ranking/{season_id}/{rst}/{ts}/pdetail-{i}'
        req = urllib.request.Request(url, headers = req_header)
        with urllib.request.urlopen(req) as res:
            pdetail = json.load(res)
        pokedata.update(pdetail)
    with open(MAINPATH+'/pokedetail'+str(battle_rule)+'.picke', mode='wb') as f:
        pickle.dump(pokedata, f)
    return 1

def load_pokeinfo(name, battle_rule):
    MAINPATH = os.path.dirname(os.path.abspath(__file__))
    with open(MAINPATH+'/pokedetail'+str(battle_rule)+'.picke', 'rb') as f:
        pokedata = pickle.load(f)
    with open(MAINPATH+'/pokedex.pickle', 'rb') as f:
        pokedex = pickle.load(f)
        pokenames = pokedex['poke']

    pokelist = []
    pnum = -1
    for i in pokedata.keys():
        if (pokenames[int(i)-1] == name):
            pnum = i
            target_poke = pokedata[i]
            break
    if (pnum == -1):
        return 0
    for form_id in target_poke.keys():
        pname = name + form_id
        pokewaza = []
        for pwaza in pokedata[pnum][form_id]['temoti']['waza']:
            value = {'tag':pokedex['waza'][int(pwaza['id'])], 'val':pwaza['val']}
            pokewaza.append(value)
        poketokusei = []
        for pwaza in pokedata[pnum][form_id]['temoti']['tokusei']:
            value = {'tag':pokedex['tokusei'][int(pwaza['id'])], 'val':pwaza['val']}
            poketokusei.append(value)
        pokeitem = []
        for pwaza in pokedata[pnum][form_id]['temoti']['motimono']:
            value = {'tag':pokedex['item'][int(pwaza['id'])], 'val':pwaza['val']}
            pokeitem.append(value)
        pokeseikaku = []
        for pwaza in pokedata[pnum][form_id]['temoti']['seikaku']:
            value = {'tag':pokedex['seikaku'][int(pwaza['id'])], 'val':pwaza['val']}
            pokeseikaku.append(value)
        pokelist.append({'move':pokewaza, 'abl':poketokusei, 'ite':pokeitem, 'nature':pokeseikaku})
    return pokelist

def make_str(l):
    txt = ''
    i = 1
    for s in l:
        txt += str(i)+'.'+str(s['tag'])+':'+str(s['val'])+'%\n'
        i+=1
    return txt

async def get_rank(ctx, rate, battle_rule):
    old_ts = load_update_time(battle_rule)
    ts, rst, season_id = await create_request(battle_rule)
    if (old_ts[0] != ts[0]):
        success = await get_trainer(ts[0], rst, season_id, battle_rule)
        if (success == 0):
            return 0
    ranking_list = load_trainer(battle_rule)
    rank = ranking_search(ranking_list, rate)+1
    save_update_time([ts[0], old_ts[1]], battle_rule)
    dt = datetime.datetime.fromtimestamp(ts[0])

    if (rate > ranking_list[len(ranking_list)-1]):
        await ctx.send(f'{ctx.author.mention} ランキング圏外です（'+str(dt)+'）')
    else:
        await ctx.send(f'{ctx.author.mention} '+str(rank)+'位です（'+str(dt)+'）')
    return 1

async def get_rate(ctx, rank, battle_rule):
    old_ts = load_update_time(battle_rule)
    ts, rst, season_id = await create_request(battle_rule)
    if (old_ts[0] != ts[0]):
        success = await get_trainer(ts[0], rst, season_id, battle_rule)
        if (success == 0):
            return 0
    ranking_list = load_trainer(battle_rule)    
    save_update_time([ts[0], old_ts[1]], battle_rule)
    dt = datetime.datetime.fromtimestamp(ts[0])
    if (rank > len(ranking_list) or rank < 1):
        await ctx.send(f'{ctx.author.mention} レートは不明です（'+str(dt)+'）')
    else:
        await ctx.send(f'{ctx.author.mention} レートは約'+str(ranking_list[rank-1]/1000)+'です（'+str(dt)+'）')
    return 1

async def pokerank(ctx, rank, battle_rule):
    fpath = os.path.dirname(os.path.abspath(__file__))+'/pokerank'+str(battle_rule)+'.pickle'
    old_ts = load_update_time(battle_rule)
    ts, rst, season_id = await create_request(battle_rule)
    if (old_ts[1] != ts[1] or os.path.exists(fpath) == False):
        success = await get_pokerank(ts[1], rst, season_id, battle_rule)
        if (success == 0):
            return []
    ranking_list = load_pokerank(rank, battle_rule)
    save_update_time([old_ts[0], ts[1]], battle_rule)
    return ranking_list, str(datetime.datetime.fromtimestamp(ts[1]))

async def pokeinfo(ctx, name, battle_rule):
    fpath = os.path.dirname(os.path.abspath(__file__))+'/pokerank'+str(battle_rule)+'.pickle'
    old_ts = load_update_time(battle_rule)
    ts, rst, season_id = await create_request(battle_rule)
    if (old_ts[1] != ts[1] or os.path.exists(fpath) == False):
        success = await get_pokerank(ts[1], rst, season_id, battle_rule)
        if (success == 0):
            return []
    pinfo = load_pokeinfo(name, battle_rule)
    for pi in pinfo:
        embed = discord.Embed(title=name)
        embed.add_field(name = '性格', value = make_str(pi['nature']), inline = True)
        embed.add_field(name = '特性', value = make_str(pi['abl']), inline = True)
        embed.add_field(name = '持ち物', value = make_str(pi['ite']), inline = True)
        embed.add_field(name = '技', value = make_str(pi['move']), inline = True)
        await ctx.send(f'{ctx.author.mention} ', embed = embed)
    save_update_time([old_ts[0], ts[1]], battle_rule)
    return [0], str(datetime.datetime.fromtimestamp(ts[1]))
