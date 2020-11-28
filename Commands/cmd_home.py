import urllib.request
import json
import gzip
import os
import datetime
import pickle

def load_update_time():
    fpath = os.path.dirname(os.path.abspath(__file__))+'/HomeUpdateTime.txt'
    ts = [0,0]
    if (os.path.exists(fpath)):
        with open(fpath, 'r') as f:
            data = f.read()
        ts_str = data.split(',')
        ts = [int(ts_str[0]), int(ts_str[1])]
    return ts

def save_update_time(ts):
    fpath = os.path.dirname(os.path.abspath(__file__))+'/HomeUpdateTime.txt'
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

def load_trainer():
    MAINPATH = os.path.dirname(os.path.abspath(__file__))
    body = ''
    with gzip.open(MAINPATH+'/trainer.json.gz', mode='rt', encoding='utf-8') as f:
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


async def get_trainer(ts, rst, season_id):
    url = 'https://resource.pokemon-home.com/battledata/ranking/'+str(season_id)+'/'+str(rst)+'/'+str(ts)+'/traner-1'
    MAINPATH = os.path.dirname(os.path.abspath(__file__))
    try:
        with urllib.request.urlopen(url) as web_file:
            data = web_file.read()
            with open(MAINPATH+'/trainer.json.gz', mode='wb') as local_file:
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
    return 1


async def get_rank(ctx, rate, battle_rule):
    old_ts = load_update_time()
    ts, rst, season_id = await create_request(battle_rule)
    if (old_ts[0] != ts[0]):
        success = await get_trainer(ts[0], rst, season_id)
        if (success == 0):
            return 0
    ranking_list = load_trainer()
    rank = ranking_search(ranking_list, rate)+1
    save_update_time([ts[0], old_ts[1]])
    dt = datetime.datetime.fromtimestamp(ts[0])

    if (rate > ranking_list[len(ranking_list)-1]):
        await ctx.send(f'{ctx.author.mention} ランキング圏外です（'+str(dt)+'）')
    else:
        await ctx.send(f'{ctx.author.mention} '+str(rank)+'位です（'+str(dt)+'）')
    return 1

async def get_rate(ctx, rank, battle_rule):
    
    old_ts = load_update_time()
    ts, rst, season_id = await create_request(battle_rule)
    if (old_ts[0] != ts[0]):
        success = await get_trainer(ts[0], rst, season_id)
        if (success == 0):
            return 0
    ranking_list = load_trainer()    
    save_update_time([ts[0], old_ts[1]])
    dt = datetime.datetime.fromtimestamp(ts[0])
    if (rank > len(ranking_list) or rank < 1):
        await ctx.send(f'{ctx.author.mention} レートは不明です（'+str(dt)+'）')
    else:
        await ctx.send(f'{ctx.author.mention} レートは約'+str(ranking_list[rank-1]/1000)+'です（'+str(dt)+'）')
    return 1

async def pokerank(ctx, rank, battle_rule):
    fpath = os.path.dirname(os.path.abspath(__file__))+'/pokerank'+str(battle_rule)+'.pickle'
    old_ts = load_update_time()
    ts, rst, season_id = await create_request(battle_rule)
    if (old_ts[1] != ts[1] or os.path.exists(fpath) == False):
        success = await get_pokerank(ts[1], rst, season_id, battle_rule)
        if (success == 0):
            return []
    ranking_list = load_pokerank(rank, battle_rule)
    save_update_time([old_ts[0], ts[1]])
    return ranking_list, str(datetime.datetime.fromtimestamp(ts[1]))
