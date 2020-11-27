import urllib.request
import json
import gzip

def calc_seasonid(season, battle_rule):
    return 10000 + season * 10 + battle_rule

def ranking_search(_list, value_):
    length = len(_list)
    value = value_*1000
    print(str(_list[0])+':'+str(_list[length-1]))
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

async def get_trainer(ts, rst, season_id):
    url = 'https://resource.pokemon-home.com/battledata/ranking/'+str(season_id)+'/'+str(rst)+'/'+str(ts)+'/traner-1'
    body = ''
    try:
        with urllib.request.urlopen(url) as web_file:
            data = web_file.read()
            with open('trainer.json.gz', mode='wb') as local_file:
                local_file.write(data)
        with gzip.open('trainer.json.gz', mode='rt', encoding='utf-8') as f:
            data = f.read()
            body = json.loads(data)
    except urllib.error.URLError as e:
        print(e)
    rate = []
#    print(body)
    for r in body:
        rate.append(int(r['rating_value']))
    return rate

async def get_rank(ctx, rate, battle_rule):
    ts, rst, season_id = await create_request(battle_rule)
    ranking_list = await get_trainer(ts[0], rst, season_id)
    rank = ranking_search(ranking_list, rate)+1
    await ctx.send(f'{ctx.author.mention} '+str(rank)+'位です')
    return

async def get_rate(ctx, rank, battle_rule):
    ts, rst, season_id = await create_request(battle_rule)
    ranking_list = await get_trainer(ts[0], rst, season_id)
    await ctx.send(f'{ctx.author.mention} レートは約'+str(ranking_list[rank-1]/1000)+'です')
    return
